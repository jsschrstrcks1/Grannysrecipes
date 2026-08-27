# Unfinished Tasks

| library_task_id | priority | title |
|---|---|---|
| audit0827-gny-index-stale-17-recipes | 1 | P1 AUDIT-0827: granny/recipes_master.json (201 recipes, updated 2026-07-29) vs recipes-index.json + 10 shards (184, dated 2026-01-23): 17 transcribed recipes never render because script.js:95 loads the index and only falls back on fetch failure. The Rebuild Indexes workflow evidently never completed for the 2026-07-29 push. Re-run sharding, verify the workflow trigger, and confirm the 17 named recipes appear. |

<!-- library register 2026-08-27T05:05:31.510Z -->
| audit0827-gny-scan-suffix-bug | 1 | P1 AUDIT-0827: renderOriginalScan (script.js:823-827) builds 'granny/&lt;ref&gt; Medium.jpeg'; no '*Medium*' files exist on disk — 0 of 313 refs resolve, 252 would resolve as plain .jpeg; the ternary at 824-826 is a no-op half-finished IMG_ special case, and granny/image_classification.json is keyed on the same dead convention. One-token fix + manifest re-key. |

<!-- library register 2026-08-27T05:05:31.911Z -->
| audit0827-gny-untranscribed-flagged-recipes | 2 | P2 AUDIT-0827: 4 recipes ship with 0 ingredients AND 0 instructions (fish-is-good-food-collection, pumpkin-apple-spice-muffins, yucatan-grilled-pork, rice-pudding-lactaid — currently hidden by the stale index, they surface as empty pages the moment it rebuilds); 5 more are NEEDS_MANUAL_REVIEW (quiche-crepes 'Step 2 is incoherent'), 4 needs-transcription, 2 partial, 11 low-confidence, 5 with [UNCLEAR]. Transcribe/repair before or with the index rebuild. |

<!-- library register 2026-08-27T05:05:32.311Z -->
| audit0827-gny-overlooked-tips-unapplied | 2 | P2 AUDIT-0827: OVERLOOKED_TIPS_REPORT.md (2026-01-10) identifies 27 tips/attributions/family sentiments missing from recipes_master.json with the exact JSON to paste, never applied (spot-checked lime-coconut-salad still lacks its notes). Apply the 27 blocks. Related: Granny has no tips surface at all and aggregate_tips.py in the hub pulls only MomsRecipes+Allrecipes — include Granny. |

<!-- library register 2026-08-27T05:05:32.714Z -->
| audit0827-gny-memorial-unreachable | 3 | P3 AUDIT-0827: Memorial/Grandma/ (618 files incl. 10 videos) is documented as a first-class section (README.md:18,74,152-155) but no page displays it — possibly deliberate (appendix: 'do NOT publish without consent'). Operator decision: build the gated memorial page or mark the directory explicitly private-by-design. |

<!-- library register 2026-08-27T05:05:33.103Z -->
| audit0827-gny-auth-gate-wrong-question | 3 | P3 AUDIT-0827: the auth gate on Granny Hudson's site still asks 'What is Grandma's last name?' (index.html:22, recipe.html:22) — borrowed wholesale from Grandmasrecipes and never localised. Fix the prompt text (the shared AUTH_KEY/answer is the separate household-wide task). |

<!-- library register 2026-08-27T05:05:33.501Z -->
| audit0827-gny-unread-generated-data | 3 | P3 AUDIT-0827: granny/ingredient-index.json (81 KB) is rebuilt by CI and fetched by nothing (no ingredient-search UI here, unlike the hub); granny/collections.json is unread at runtime and wrong (recipe_count 91 vs 184/201); ingredient_list.md has no consumer; image manifests + processed/ (160 files) published with no referencing page. Wire or stop generating. |
