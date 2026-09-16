## What this changes

<!-- One or two sentences. Name the page or the check, and whether it is curated here or assembled. -->

## Why

<!--
The reasoning, not the diff. For a curated page: what a reader could not work out before. For a
pin: which upstream release the site should now be describing. For a check: the class of defect it
makes impossible.
-->

## Which of these applies

<!-- Tick every one that applies, then answer the question underneath it. -->

- [ ] **A pinned revision moved.** Say which repositories moved, to which tags, and what changed in what the site now shows. Pages under `runner/` and `spec/` are assembled from these, so this is the pull request that changes them.
- [ ] **A curated page states a figure.** Say which artefact owns that figure and paste the check output that keeps the two in step. A figure restated in prose with no check behind it is how this repository came to publish numbers that had stopped being true.
- [ ] **A curated page was added.** Say where it sits in the navigation, and why it is not a restatement of a document this site assembles.
- [ ] **The pitch is referenced.** Confirm the playback link points at this site rather than at a release asset, and that the archival link uses the immutable tag. A release asset is served `content-disposition: attachment`, so a link to one downloads 15 MB instead of playing it — a defect that shipped once, past every header check that existed.
- [ ] **A check was changed or added.** Say what it now fails on that it did not, and why that was a gap.
- [ ] **Build, pins or process only.** Nothing a reader sees changed.

## Validation

<!--
Run these and paste the result. The four pure checks need nothing installed beyond PyYAML and run
in about a second; `build-site.sh` is the one that catches a reference to a page or anchor that
does not exist, because the site is built with `strict: true`.
-->

```
python3 scripts/check-external-links.py
python3 scripts/check-nav.py
python3 scripts/check-pitch-references.py
python3 scripts/check-workflows.py
./scripts/build-site.sh site
```

## Does any of this imply a security guarantee?

- [ ] No. Conformance is not a security property, and nothing here presents it as one.

<!--
If you cannot tick that, say why in the box below. This site explains how to measure defined
behavioural compatibility against a stated profile. It does not audit, and a passing result must
never be described as making a contract safe.
-->
