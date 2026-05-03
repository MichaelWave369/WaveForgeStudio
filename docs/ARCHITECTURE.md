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

searchable gallery
  -> curated collection manifest
  -> collection index
  -> showcase / playlist / release set

curated collection manifest
  -> portable collection export
  -> selected preview ZIPs
  -> collection export manifest/receipt
  -> share/archive release pack

collection export pack
  -> alpha release deck
  -> offline HTML cards + Markdown deck
  -> showcase / presentation artifact

alpha release deck
  -> deterministic release deck ZIP
  -> release deck ZIP manifest/receipt
  -> share/archive showcase artifact

runs root
  -> gallery
  -> collection
  -> collection export
  -> release deck
  -> release deck ZIP
  -> unified release build manifest/receipt

unified release build
  -> deterministic release build ZIP
  -> release build ZIP manifest/receipt
  -> top-level share/archive artifact

release build ZIP
  -> release build verification report
  -> verification receipt
  -> local auditor seal

release build verification report
  -> release certificate
  -> certificate receipt
  -> human-readable integrity certificate

release certificate
  -> certificate bundle
  -> compact proof packet
  -> certificate bundle manifest/receipt
