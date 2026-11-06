# Report contract

JSON version1.0.0 records configured limits, a summary, individual image records, duplicate/candidate pairs and unused mapping paths. Paths are relative to the chosen root. Pixel dimensions refer to the orientation-corrected view. `flags` are independent categories; one file may have several. Machine JSON omits thumbnail payloads, while the standalone HTML embeds small JPEG previews.

Pairs record `exact_duplicate` or `visual_candidate`, hash distance and whether both known property IDs differ. Candidate similarity is not proof of identity. Zero distance can occur for unrelated simple images. The tool never chooses which original to delete.
