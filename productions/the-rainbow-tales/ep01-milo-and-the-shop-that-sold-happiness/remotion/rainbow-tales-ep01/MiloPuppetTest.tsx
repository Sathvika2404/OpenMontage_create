// 15-second puppet test: Milo on a warm cream backdrop, driven entirely by the
// explicit action timeline passed in as props.

import React, { useMemo } from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { MiloPuppet, MiloRig } from "./MiloPuppet";
import { ActionTimeline, compileTimeline } from "./timeline";

export type MiloPuppetTestProps = {
  rig: MiloRig;
  timeline: ActionTimeline;
};

const FLOOR_Y = 985; // where Milo's paws touch the floor, in frame px

export const MiloPuppetTest: React.FC<MiloPuppetTestProps> = ({ rig, timeline }) => {
  const frame = useCurrentFrame();
  const ev = useMemo(() => compileTimeline(timeline), [timeline]);
  const v = (ch: string) => ev(ch, frame);

  const pose = {
    breath: v("body.breath"),
    headRotate: v("head.rotate"),
    headX: v("head.x"),
    headY: v("head.y"),
    earLeft: v("ear_left.rotate"),
    earRight: v("ear_right.rotate"),
    tail: v("tail.rotate"),
    bandana: v("bandana.rotate"),
    eyeLeft: v("eye_left.closure"),
    eyeRight: v("eye_right.closure"),
    mouthOpen: v("mouth.open"),
  };

  const left = 960 - rig.pivots.body[0];
  const top = FLOOR_Y - rig.canvas.height;
  // Camera pushes in toward Milo's face (head pivot sits under the chin).
  const focusX = 960;
  const focusY = top + rig.pivots.head[1] - 120 + v("camera.focus_y");
  const scale = v("camera.scale");

  return (
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(ellipse 75% 70% at 50% 42%, #FBF3E6 0%, #F5E8D4 62%, #EEDCC3 100%)",
      }}
    >
      <AbsoluteFill
        style={{
          transformOrigin: `${focusX}px ${focusY}px`,
          transform: `scale(${scale})`,
        }}
      >
        {/* Soft contact shadow so Milo sits on the floor rather than floating. */}
        <div
          style={{
            position: "absolute",
            left: 960 - 250,
            top: FLOOR_Y - 34,
            width: 500,
            height: 64,
            borderRadius: "50%",
            background:
              "radial-gradient(ellipse at center, rgba(120,84,48,0.30) 0%, rgba(120,84,48,0.12) 45%, rgba(120,84,48,0) 72%)",
          }}
        />
        <div style={{ position: "absolute", left, top }}>
          <MiloPuppet rig={rig} pose={pose} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
