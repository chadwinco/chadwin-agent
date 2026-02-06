# GOAL
- Automate the research process for identifying and valuing companies which have the potential for long-term value creation
- Using SEC filings, financial statements, earning call transcripts, and third-party information, the research should aim to identify companies with three primary characteristics:
  - Strong, predictable cash generation
  - Sustainably high returns on capital
  - Attractive growth opportunities
- The output of the research process should be:
  - A fair-price estimate based on a long-term view of the company
  - A concise write-up that describes the competitive position of the company and whether the current price leaves a meaningful margin of safety

# DATA
- In the `companies` directory, there are sub-directories which contain relevant data for a given company
- This data should be the foundation of the research process, with web search used to fill in any missing gaps
- All reports on a given company should be placed in the `analysis` directory for that company. The reports should be written in well-structured markdown

# PROCESS
- You are responsible for boostrapping the research workflow from stratch, aiming toward the goals described above
- You should use this repo as the place to document processes, build re-usable workflows, and write detailed prompts which will be executed to achieve the research goals
- Your goal at all times should be to improve the methods you use, looking carefully at the outputs from the research and looking for improvements which are then documenting and used on subsequent researh

# PYTHON ENV
- Use a local virtual environment stored at `.venv/` for all Python work.
- Create it with `python3 -m venv .venv` and activate it before running scripts.
