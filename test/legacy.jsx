  import React, { Suspense, useRef, useEffect, useState } from "react";
  import { Canvas, useFrame } from "@react-three/fiber";
  import { OrbitControls } from "@react-three/drei";
  import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
  import { VRMLoaderPlugin } from "@pixiv/three-vrm";
  import * as THREE from "three";
  import { socket } from "./socket";

  //  VRMModel Component 
  function VRMModel({ url, controls }) {
    const group = useRef();
    const vrmRef = useRef(null);
    const blendMapRef = useRef({});
    const blendNamesRef = useRef([]);
    const resolved = useRef({ blink: [], brow: {}, all: {}, mouth: {}, hair: {} });
    const boneMap = useRef({});

    const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));

    // Load VRM 
    useEffect(() => {
      const loader = new GLTFLoader();
      loader.register((parser) => new VRMLoaderPlugin(parser));

      let mounted = true;
      loader.load(
        url,
        (gltf) => {
          if (!mounted) return;
          const loadedVrm = gltf.userData?.vrm;
          if (!loadedVrm) return;

          loadedVrm.scene.rotation.y = Math.PI;
          group.current.add(loadedVrm.scene);
          vrmRef.current = loadedVrm;

          // Bones
          const map = {};
          Object.entries(loadedVrm.humanoid.humanBones).forEach(([k, b]) => {
            if (b?.node) map[k] = b.node;
          });
          boneMap.current = map;

          // BlendShapes
          const blendMap = {};
          loadedVrm.scene.traverse((node) => {
            if ((node.isMesh || node.isSkinnedMesh) && node.morphTargetDictionary) {
              Object.entries(node.morphTargetDictionary).forEach(([name, idx]) => {
                if (!blendMap[name]) blendMap[name] = [];
                blendMap[name].push({ mesh: node, index: idx });
              });
            }
          });
          blendMapRef.current = blendMap;
          blendNamesRef.current = Object.keys(blendMap);

          // Resolve names
          const names = blendNamesRef.current;
          const r = { blink: [], brow: {}, all: {}, mouth: {}, hair: {} };
          names.forEach((n) => {
            if (/blink|close/i.test(n)) r.blink.push(n);
            if (/BRW_/i.test(n)) r.brow[n] = n;
            if (/ALL_/i.test(n)) r.all[n] = n;
            if (/MTH_/i.test(n)) r.mouth[n] = n;
            if (/HA_/i.test(n)) r.hair[n] = n;
          });
          resolved.current = r;
        },
        undefined,
        console.error
      );

      return () => (mounted = false);
    }, [url]);

    // - Helpers 
    const setBlend = (name, val) => {
      const arr = blendMapRef.current[name];
      if (!arr) return;
      arr.forEach(({ mesh, index }) => (mesh.morphTargetInfluences[index] = clamp(val, 0, 1)));
    };

    const setRotation = (boneName, x = 0, y = 0, z = 0, smooth = 0.12) => {
      const bone = boneMap.current[boneName];
      if (!bone) return;
      const target = new THREE.Euler(x, y, z, "XYZ");
      bone.quaternion.slerp(new THREE.Quaternion().setFromEuler(target), smooth);
    };

    // Animation Loop 
    const blinkCurrent = useRef(0);
    const headIdle = useRef({ x: 0, y: 0 });
    const lerp = (a, b, t) => a + (b - a) * t;

    useFrame(() => {
      if (!vrmRef.current) return;
      const s = controls;
      const r = resolved.current;

      // Bones
      setRotation("head", s.headX, s.headY, s.headZ);
      setRotation("spine", s.spineX, s.spineY, s.spineZ);
      setRotation("leftUpperArm", s.leftArmX, s.leftArmY, s.leftArmZ);
      setRotation("rightUpperArm", s.rightArmX, s.rightArmY, s.rightArmZ);
      setRotation("leftUpperLeg", s.leftLegX, s.leftLegY, s.leftLegZ);
      setRotation("rightUpperLeg", s.rightLegX, s.rightLegY, s.rightLegZ);

      // Blink
      const blinkTarget = s.blinkToggle ? s.blinkIntensity : 0;
      blinkCurrent.current = lerp(blinkCurrent.current, blinkTarget, 0.35);
      r.blink.forEach((name) => setBlend(name, blinkCurrent.current));

      // Emotions
      Object.keys(r.all).forEach((name) => {
        const key = name.split("_ALL_")[1].toLowerCase();
        const val = s.emotions[key] ? s.emotionIntensity : 0;
        setBlend(name, val);
      });
      Object.keys(r.brow).forEach((name) => {
        const key = name.split("_BRW_")[1].toLowerCase();
        const val = s.emotions[key] ? s.emotionIntensity : 0;
        setBlend(name, val);
      });
      Object.keys(r.mouth).forEach((name) => {
        const key = name.split("_MTH_")[1].toUpperCase();
        const val = s.mouth[key] ?? 0;
        setBlend(name, val);
      });

      // Idle sway
      const now = Date.now();
      headIdle.current.x = lerp(headIdle.current.x, Math.sin(now * 0.001) * 0.03, 0.05);
      headIdle.current.y = lerp(headIdle.current.y, Math.sin(now * 0.0015) * 0.05, 0.05);
      group.current.rotation.x = headIdle.current.x;
      group.current.rotation.y = Math.PI + headIdle.current.y;
    });

    return <group ref={group} />;
  }

  // ------------------- Control Panel -------------------
  export default function ModelViewerWithControls() {
    const [showControls, setShowControls] = useState(true);

    const initialControls = {
      headX: 0, headY: 0, headZ: 0,
      spineX: 0, spineY: 0, spineZ: 0,
      leftArmX: 0, leftArmY: 0, leftArmZ: 0,
      rightArmX: 0, rightArmY: 0, rightArmZ: 0,
      leftLegX: 0, leftLegY: 0, leftLegZ: 0,
      rightLegX: 0, rightLegY: 0, rightLegZ: 0,
      blinkToggle: true,
      blinkIntensity: 0.8,
      emotionIntensity: 0.8,
      emotions: { angry: false, fun: false, joy: false, sorrow: false, surprised: false },
      mouth: { A: 0, I: 0, U: 0, E: 0, O: 0 },
    };

    const [controls, setControls] = useState(initialControls);
    const [ttsText, setTtsText] = useState("");

    //  Socket Two-Way 
    useEffect(() => {
      const handler = (data) => setControls((prev) => ({ ...prev, ...data }));
      socket.on("update_controls", handler);
      return () => {
      socket.off("update_controls", handler);
    };
  }, []);



    const updateControls = (newControls) => {
      setControls(newControls);
      socket.emit("controls_update", newControls);
    };

    const createSlider = (label, min, max, step, value, onChange) => (
      <div style={{ display: "flex", alignItems: "center", margin: "2px 0" }}>
        <label style={{ width: "100px" }}>{label}</label>
        <input type="range" min={min} max={max} step={step} value={value} onChange={onChange} style={{ flex: 1 }} />
        <span style={{ width: "40px", textAlign: "right" }}>{parseFloat(value).toFixed(2)}</span>
      </div>
    );

    const triggerHelloWorld = () => {
      if (ttsText.trim() === "") return;
      console.log("🖥️ Triggering Hello World with:", ttsText);
      socket.emit("hello_world", { text: ttsText });
      setTtsText("");
    };

    return (
      <div style={{ display: "flex", height: "100vh", position: "relative" }}>
        {/* Toggle Button */}
        <button
          onClick={() => setShowControls(!showControls)}
          style={{
            position: "absolute",
            top: "10px",
            left: "10px",
            zIndex: 1000,
            padding: "6px 12px",
            borderRadius: "6px",
            background: "#444",
            color: "#fff",
            border: "none",
            cursor: "pointer",
          }}
        >
          {showControls ? "← Hide" : "→ Show"}
        </button>

        {/* Sliding Panel */}
        <div
          style={{
            width: "350px",
            padding: "10px",
            background: "#222",
            color: "#fff",
            overflowY: "scroll",
            transition: "transform 0.3s ease",
            transform: showControls ? "translateX(0)" : "translateX(-100%)",
            position: "absolute",
            top: 0,
            left: 0,
            height: "100%",
            zIndex: 999,
          }}
        >
          <h3>Text-to-Speech</h3>
          <input
            type="text"
            value={ttsText}
            onChange={(e) => setTtsText(e.target.value)}
            placeholder="Type something..."
            style={{ width: "100%", marginBottom: "6px" }}
          />
          <button onClick={triggerHelloWorld} style={{ width: "100%", padding: "6px", background: "#444", color: "#fff", border: "none" }}>
            Speak
          </button>

          <h3>Body Controls</h3>
          {["X", "Y", "Z"].map((axis) =>
            createSlider(`Head ${axis}`, -0.5, 0.5, 0.01, controls[`head${axis}`], (e) =>
              updateControls({ ...controls, [`head${axis}`]: parseFloat(e.target.value) })
            )
          )}
          {["X", "Y", "Z"].map((axis) =>
            createSlider(`Spine ${axis}`, -0.5, 0.5, 0.01, controls[`spine${axis}`], (e) =>
              updateControls({ ...controls, [`spine${axis}`]: parseFloat(e.target.value) })
            )
          )}
          {["X", "Y", "Z"].map((axis) =>
            createSlider(`Left Arm ${axis}`, -1, 1, 0.01, controls[`leftArm${axis}`], (e) =>
              updateControls({ ...controls, [`leftArm${axis}`]: parseFloat(e.target.value) })
            )
          )}
          {["X", "Y", "Z"].map((axis) =>
            createSlider(`Right Arm ${axis}`, -1, 1, 0.01, controls[`rightArm${axis}`], (e) =>
              updateControls({ ...controls, [`rightArm${axis}`]: parseFloat(e.target.value) })
            )
          )}
          {["X", "Y", "Z"].map((axis) =>
            createSlider(`Left Leg ${axis}`, -1, 1, 0.01, controls[`leftLeg${axis}`], (e) =>
              updateControls({ ...controls, [`leftLeg${axis}`]: parseFloat(e.target.value) })
            )
          )}
          {["X", "Y", "Z"].map((axis) =>
            createSlider(`Right Leg ${axis}`, -1, 1, 0.01, controls[`rightLeg${axis}`], (e) =>
              updateControls({ ...controls, [`rightLeg${axis}`]: parseFloat(e.target.value) })
            )
          )}

          <h3>Blink</h3>
          <label style={{ display: "flex", alignItems: "center", margin: "2px 0" }}>
            <input
              type="checkbox"
              checked={controls.blinkToggle}
              onChange={(e) => updateControls({ ...controls, blinkToggle: e.target.checked })}
            />
            <span style={{ marginLeft: "8px" }}>Blink Toggle</span>
          </label>
          {createSlider("Blink Intensity", 0, 1, 0.01, controls.blinkIntensity, (e) =>
            updateControls({ ...controls, blinkIntensity: parseFloat(e.target.value) })
          )}

          <h3>Emotions</h3>
          {createSlider("Emotion Intensity", 0, 1, 0.01, controls.emotionIntensity, (e) =>
            updateControls({ ...controls, emotionIntensity: parseFloat(e.target.value) })
          )}
          {Object.keys(controls.emotions).map((key) => (
            <label key={key} style={{ display: "flex", alignItems: "center" }}>
              <input
                type="checkbox"
                checked={controls.emotions[key]}
                onChange={(e) =>
                  updateControls({ ...controls, emotions: { ...controls.emotions, [key]: e.target.checked } })
                }
              />
              <span style={{ marginLeft: "6px" }}>{key.charAt(0).toUpperCase() + key.slice(1)}</span>
            </label>
          ))}

          <h3>Mouth / Visemes</h3>
          {Object.keys(controls.mouth).map((key) =>
            createSlider(key, 0, 1, 0.01, controls.mouth[key], (e) =>
              updateControls({ ...controls, mouth: { ...controls.mouth, [key]: parseFloat(e.target.value) } })
            )
          )}
        </div>

        {/* Canvas */}
        <Canvas camera={{ position: [0, 1.5, 3], fov: 50 }} style={{ flex: 1 }}>
          <ambientLight intensity={0.8} />
          <directionalLight position={[0, 3, 5]} intensity={1.0} />
          <Suspense fallback={null}>
            <VRMModel url="/AvatarSample_H.vrm" controls={controls} />
          </Suspense>
          <OrbitControls />
        </Canvas>
      </div>
    );
  }
