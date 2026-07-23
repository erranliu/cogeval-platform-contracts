# COG Cases current (v3)

`cogeval.cog_case.v3` is the only published COG Case contract.

`cog_case_display_id` is required and is the stable product identity used in
all user-visible case selection, display, communication, run metadata, and
result references. It is exact, unique among active published cases, immutable
after publication, and must not be reused for another case.

`source_id` and `external_id` remain required payload facts for source access,
execution materialization, and platform result routing. They are internal
technical coordinates and must not replace `cog_case_display_id` in external
product surfaces.

The v3 payload also carries the v2 `environment_requirements` declaration.
The platform declares required resources; Workbench owns local probing and
readiness decisions.
