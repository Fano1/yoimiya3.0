import ModelViewer from "./components/Exp";
import WaifuModel from './components/Waifu'
import VRMDebug from './components/Component'
import React, { useState } from "react";

export default function App() {
  const [isSpeaking, setIsSpeaking] = useState(false);
  return (
    <>
      {/* <VRMDebug url="/AvatarSample_H.vrm" /> */}
      {/* <div style={{ width: "100vw", height: "100vh", background: "#222" }}> */}
      {/* <ModelViewer /> */}
    {/* </div> */}

        <div style={{zIndex: -1, width: '100vw', height: '100vh'}}><WaifuModel /></div>
      </>
  )
}


