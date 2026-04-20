# OS Process Scheduler Simulator

A desktop GUI application for visualizing and comparing CPU scheduling algorithms used in Operating Systems. The project is built with Python and Tkinter and is designed for demonstrations, mini-project submissions, and quick algorithm analysis.

## Features

- Interactive GUI for entering, editing, and deleting processes
- Support for multiple CPU scheduling algorithms
- Gantt chart visualization
- Detailed per-process results
- Average performance metrics
- Algorithm comparison table
- CSV export for current results and comparison output
- Demo testcase loader for quick presentation

## Implemented Algorithms

- First Come First Serve (FCFS)
- Shortest Job First (Non-Preemptive)
- Longest Job First (Non-Preemptive)
- Shortest Remaining Time First (Preemptive SJF)
- Priority Scheduling (Non-Preemptive)
- Priority Scheduling (Preemptive)
- Round Robin

## Tech Stack

- Python
- Tkinter
- ttk

## Team Members

| Name | Roll No | Department | Semester |
|------|---------|------------|----------|
| Hemang Mistry | 14885 | BTech CE | 4th |
| Pari Barot | 15704 | BTech CE | 4th |

## Project Structure

```text
os scheduler simulator/
|-- algorithms/
|-- core/
|-- gui/
|   |-- app.py
|   `-- theme.py
|-- main.py
|-- README.md
`-- dist/
```

## Run Locally

Open PowerShell in the project root and run:

```powershell
cd "D:\os scheduler simulator"
python -m gui.app
```

If `python` is not available, use:

```powershell
py -m gui.app
```

## Build Executable

Install PyInstaller:

```powershell
python -m pip install pyinstaller
```

Build the desktop executable:

```powershell
python -m PyInstaller --onefile --windowed --name "OS Scheduler Simulator" gui\app.py
```

After the build completes, the executable will be available in:

- `dist/OS Scheduler Simulator.exe`

## Download and Release

To share the project with others:

1. Build the `.exe`
2. Put the executable in a release folder
3. Add a short `README.txt`
4. Compress the folder into a `.zip`
5. Upload it to:
   - GitHub Releases, or
   - Google Drive

Recommended GitHub release title:

```text
OS Scheduler Simulator v1.0.0
```

## Release Download

You can download the packaged desktop build from the GitHub Releases page:

- [Download from Releases](https://github.com/hemangmistry111-collab/os-scheduler-simulator/releases)

Suggested user flow:

1. Open the Releases page
2. Download the latest `.zip` file
3. Extract the archive
4. Run `OS Scheduler Simulator.exe`

If Windows shows a security prompt, choose `More info` and then `Run anyway` only if the file was downloaded from your official repository release.

## How to Use

1. Open the app
2. Go to the `Processes` tab
3. Add process details such as PID, arrival time, burst time, and priority
4. Move to the `Simulation` tab
5. Choose an algorithm
6. Enter time quantum for Round Robin if needed
7. Click `Simulate`
8. Review:
   - results table
   - averages
   - response time
   - CPU idle time
   - CPU utilization
   - Gantt chart
9. Open the `Comparison` tab to compare all algorithms

## Screenshots

Add project screenshots here after capturing them from the app.

Suggested screenshots:

- Home / Processes tab
- Simulation tab with Gantt chart
- Comparison tab

Example markdown once screenshots are added:

```md
![Processes Tab](screenshots/processes.png)
![Simulation Tab](screenshots/simulation.png)
![Comparison Tab](screenshots/comparison.png)
```

## Notes

- GitHub language stats were cleaned to show the real project language correctly
- Generated build files and cache files are ignored from version control

## Author

- Hemang1410
