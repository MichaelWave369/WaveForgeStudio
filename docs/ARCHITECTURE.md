# WaveForgeStudio Architecture
Prompt
  -> media packet
  -> AV timeline
  -> renderer handoff pack
  -> bridge bundles
  -> timeline preview
  -> production bundle
  -> render queue
  -> safe runner
  -> artifact ledger
  -> future guarded render execution


## First Safe Local Render Artifact Stage

AV timeline / renderer handoff
  -> local audio render stub
  -> WAV placeholders
  -> audio render receipt
  -> artifact ledger


## First Safe Local Visual Artifact Stage

AV timeline / renderer handoff
  -> local visual storyboard render stub
  -> SVG storyboard frames
  -> visual render receipt
  -> artifact ledger
