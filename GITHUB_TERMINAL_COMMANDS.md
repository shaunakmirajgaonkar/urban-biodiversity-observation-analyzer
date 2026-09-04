# GitHub Terminal Commands

```bash
cd ~/Downloads/UrbanBiodiversityObservationAnalyzer_Local
git init
git branch -M main
git add -A
git status
git commit -m "feat: add UrbanBioTrack biodiversity observation analyzer"
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/shaunakmirajgaonkar/urban-biodiversity-observation-analyzer.git
git push -u origin main
```
