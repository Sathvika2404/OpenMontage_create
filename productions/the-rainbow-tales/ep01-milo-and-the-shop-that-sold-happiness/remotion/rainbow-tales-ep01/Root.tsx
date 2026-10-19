import React from "react";
import { Composition } from "remotion";
import { MiloPuppetTest, MiloPuppetTestProps } from "./MiloPuppetTest";

// Props (rig + explicit action timeline) are supplied at render time with
// --props; see scripts/render_puppet_test.py.
const metadata = ({ props }: { props: MiloPuppetTestProps }) => ({
  fps: props.timeline?.fps ?? 30,
  durationInFrames: Math.round((props.timeline?.duration_seconds ?? 15) * (props.timeline?.fps ?? 30)),
});

export const Root: React.FC = () => (
  <>
  <Composition
    id="MiloPuppetTest"
    component={MiloPuppetTest}
    width={1920}
    height={1080}
    fps={30}
    durationInFrames={450}
    defaultProps={{} as MiloPuppetTestProps}
    calculateMetadata={metadata}
  />
  {/* Character acting test: same puppet + scene, acting timeline via --props. */}
  <Composition
    id="MiloActingTest"
    component={MiloPuppetTest}
    width={1920}
    height={1080}
    fps={30}
    durationInFrames={450}
    defaultProps={{} as MiloPuppetTestProps}
    calculateMetadata={metadata}
  />
  </>
);
