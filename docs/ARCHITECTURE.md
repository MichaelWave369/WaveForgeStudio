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


## First Local Operator Preview Stage

local audio stub + local visual storyboard
  -> local AV preview page
  -> preview manifest/receipt
  -> artifact ledger


## Portable Pack Stage

local AV preview page
  -> portable preview pack
  -> pack manifest/receipt
  -> share/archive folder

portable preview pack
  -> deterministic preview pack ZIP
  -> ZIP manifest/receipt
  -> share/archive artifact

multiple preview packs / ZIPs
  -> local demo gallery
  -> gallery manifest/receipt
  -> archive browser

multiple preview packs / ZIPs
  -> searchable local demo gallery
  -> tags / filters / hash search
  -> gallery manifest/receipt
