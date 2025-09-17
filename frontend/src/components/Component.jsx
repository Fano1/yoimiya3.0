import React, { useEffect, useState } from "react";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import { VRMLoaderPlugin } from "@pixiv/three-vrm";

export default function VRMDebug({ url }) {
  const [bones, setBones] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [meta, setMeta] = useState({});
  const [physicsBones, setPhysicsBones] = useState([]);
  const [blendShapes, setBlendShapes] = useState([]);

  useEffect(() => {
    const loader = new GLTFLoader();
    loader.register(parser => new VRMLoaderPlugin(parser));

    loader.load(
      url,
      (gltf) => {
        const vrm = gltf.userData.vrm;
        if (!vrm) {
          console.warn("No VRM found in this fucker");
          return;
        }

        // Bones
        const boneList = Object.entries(vrm.humanoid.humanBones).map(([name]) => name);
        setBones(boneList);

        // Node hierarchy
        const traverseNodes = (node, depth = 0) => {
          let result = [{ name: node.name || "Unnamed", depth }];
          node.children.forEach(child => {
            result = result.concat(traverseNodes(child, depth + 1));
          });
          return result;
        };
        setNodes(traverseNodes(vrm.scene));

        // Metadata
        setMeta(vrm.meta ? {
          name: vrm.meta.name,
          author: vrm.meta.author,
          version: vrm.meta.version,
          license: vrm.meta.licenseLabel
        } : {});

        // Physics boens (spring bones)
        const springs = Array.isArray(vrm.springBoneManager?.springBones)
          ? vrm.springBoneManager.springBones
          : [];

        const physicsList = [];
        springs.forEach(s => {
          if (s.bones && s.bones.length) {
            s.bones.forEach(b => {
              physicsList.push({
                springName: s.name || "UnnamedSpring",
                boneName: b.name,
                stiffness: s.stiffnessForce,
                drag: s.dragForce,
                gravity: s.gravityDir?.toArray?.() || [0, -1, 0],
              });
            });
          }
        });
        setPhysicsBones(physicsList);

        // BlendShapes / Morph Targets
        const blends = [];
        vrm.scene.traverse(node => {
          if ((node.isMesh || node.isSkinnedMesh) && node.morphTargetDictionary) {
            Object.keys(node.morphTargetDictionary).forEach(name => {
              blends.push({ mesh: node.name, blendShape: name });
            });
          }
        });
        setBlendShapes(blends);

        console.log("Physics bones loaded:", physicsList);
        console.log("BlendShapes loaded:", blends);
      },
      undefined,
      err => console.error(err)
    );
  }, [url]);

  return (
    <div style={{ padding: "1rem", fontFamily: "sans-serif" }}>
      <h1>VRM Debug Inspector</h1>

      <h2>Metadata</h2>
      {Object.keys(meta).length === 0 ? <p>No metadata</p> :
        <ul>
          {Object.entries(meta).map(([k,v]) => <li key={k}><strong>{k}:</strong> {v}</li>)}
        </ul>
      }

      <h2>Bones</h2>
      {bones.length === 0 ? <p>No bones found</p> :
        <ul>{bones.map(b => <li key={b}>{b}</li>)}</ul>
      }

      <h2> Node Hierarchy</h2>
      {nodes.length === 0 ? <p>No nodes</p> :
        <ul>
          {nodes.map((n,i) => (
            <li key={i} style={{ marginLeft: `${n.depth * 20}px` }}>
              {n.name}
            </li>
          ))}
        </ul>
      }

      <h2> Physics Bones (Spring Bones)</h2>
      {physicsBones.length === 0 ? <p>No physics bones found</p> :
        <ul>
          {physicsBones.map((p, i) => (
            <li key={i}>
              <strong>{p.springName}</strong> → {p.boneName} | stiffness: {p.stiffness}, drag: {p.drag}, gravity: [{p.gravity.join(", ")}]
            </li>
          ))}
        </ul>
      }

      <h2> BlendShapes / Morph Targets</h2>
      {blendShapes.length === 0 ? <p>No blend shapes found</p> :
        <ul>
          {blendShapes.map((b, i) => (
            <li key={i}>
              <strong>{b.mesh}</strong> → {b.blendShape}
            </li>
          ))}
        </ul>
      }
    </div>
  );
}
