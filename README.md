# Baker Expense Report Helper Application

Application for Baker College P-Card holders to reconcile expected expenses against actual expenses submitted through the Purchase Form.

## What This Does

This app helps match expected expenses with actual purchases by:
- Reading expense data from the spreadsheet storing Purchase Form responses
- Automatically matching expected expenses with actual transactions
- Showing you what matched, what's missing, and what's extra
- Allowing manual matching with drag-and-drop
- Generating affidavits for expenses that require them

## Getting Started

### For Non-Technical First-Time Users

#### Step 1: Install Required Software

You need two programs installed on your computer:

1. **Python 3.13 or higher**
   - Go to [python.org/downloads](https://www.python.org/downloads/)
   - Click the yellow "Download Python" button
   - Run the installer
   - **IMPORTANT**: Windows users: check the box that says "Add Python to PATH" during installation
   - Click "Install Now"

2. **Node.js 18 or higher**
   - Go to [nodejs.org](https://nodejs.org/)
   - Download the LTS (Long Term Support) version
   - Run the installer and follow the prompts

#### Step 2: Get the Code

1. Download this project as a ZIP file (or have someone send it to you)
2. **Double-click the ZIP file** to unzip/extract it

#### Step 3: Open Terminal/Command Prompt

**On Mac:**
- Press `Command + Space` to open Spotlight
- Type "Terminal" and press Enter

**On Windows:**
- Press `Windows + R`
- Type "cmd" and press Enter

#### Step 4: Navigate to the Project Folder

In the terminal, type `cd` followed by a space, then drag and drop the project folder into the terminal window. Press Enter.

For example, it might look like:
```bash
cd /Users/YourName/Desktop/expense-report-automation
```

#### Step 5: Create and Activate a Virtual Environment

Before installing Python dependencies, you need to create a virtual environment:

**On Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` appear at the beginning of your terminal prompt.

#### Step 6: Install Dependencies

Copy and paste these commands one at a time into the terminal (press Enter after each):

```bash
python3 -m pip install -r backend/requirements.txt
```

Wait for it to finish, then:

```bash
cd frontend
npm install
cd ..
npm install
```

(The frontend and backend have different dependencies, so npm install must be run in both places.)

#### Step 7: Run the App

Type this command and press Enter:
```bash
npm run dev
```

You should see messages saying the servers are starting. When you see "Local: http://localhost:5173", the app is ready.

#### Step 8: Open the App

Open your web browser (Chrome, Firefox, Safari, etc.) and go to:
```
http://localhost:5173
```

The app should now be running!

#### Step 9: Stop the App

When you're done using the app:
- Go back to the terminal window
- Press `Ctrl+C` (Windows/Mac) to stop the servers
- You can close the terminal window

### For Technical Users

#### Prerequisites

- Python 3.13+
- Node.js 18+
- npm or yarn

#### Quick Start

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
npm install

# Run dev servers
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### For Repeat Users

If you've already set up the app and just want to run it again:

1. **Open Terminal/Command Prompt** (see Step 3)
2. **Navigate to the project folder** (see Step 4)
3. **Activate the virtual environment**:
   - **Mac/Linux**: `source venv/bin/activate`
   - **Windows**: `venv\Scripts\activate`
4. **Run the app**: `npm run dev`
5. **Open your browser** to [http://localhost:5173](http://localhost:5173)

You only need to install dependencies (Step 6) once, unless the project is updated.

## How to Use

### Reconciling Expenses

1. **Select Cardholder Name**: Choose the person whose expenses you want to reconcile from the dropdown
2. **Pick Start Date**: Only transactions from this date forward will be included
3. **Paste Purchase Form Spreadsheet Link**: Link to the Google Sheets with actual purchase data
4. **Paste Expected Expenses**: Copy/paste the list of expected expenses (see format below)
5. **Click "Reconcile Expenses"**: The app processes and shows results

### Generating Affidavits (Without Reconciliation)

If you just need affidavits for all expected expenses without reconciling:

1. **Fill out all form fields** as above
2. **Click "Generate Affidavits"**: Opens a modal with all expected expenses
3. **Download individual affidavits**: Click the "Download" button next to each expense

This generates filled affidavit PDFs with the vendor, price, date, and cardholder signature.

### Expected Expenses Format

Paste expenses one per line, directly copied and pasted from Kristen's email - for example:
```
11/1/25 - Trader Joe's - $25.25
11/3/25 - Target - $9.99
11/5/25 - $15.00 - Amazon
```

Both `MM/DD/YY - Vendor - $Price` and `MM/DD/YY - $Price - Vendor` work.

## Understanding Results

The app shows three sections after reconciliation:

### ✅ Matched Expenses
Expected expenses that were successfully matched with actual transactions.

- If a matched expense requires an affidavit, you'll see a **"Download Affidavit"** link
- Click the link to generate and download a filled affidavit PDF

### ⚠️ Missing Expected Expenses
Expected expenses that weren't found in the actual transactions. You can:
- **Drag and drop** an Extra Actual card to manually match it
- Click the **✕** button to remove a manual match

### ➕ Extra Actual Expenses
Actual transactions that don't match any expected expense. These appear as draggable cards with red borders that you can drag to gray placeholder boxes.

## Manual Matching (Drag-and-Drop)

1. Scroll to the **Missing Expected Expenses** section
2. Find the expense you want to match in the **Extra Actual Expenses** section below
3. **Drag** the red-bordered card to the gray placeholder box next to the missing expense
4. To undo: click the **✕** button on the paired card

## Configuration
```

### Adjusting Matching Rules

Currently, a "match" is considered either an exact price-match or prices within a dollar and
a close lexical match between the expected and actual Vendor. If you want to change these thresholds, edit `backend/api.py` to change how strict matching is:
```python
price_tolerance=1.00       # Max price difference (in dollars)
similarity_threshold=0.75  # Min vendor name similarity (0-1)
```

## Troubleshooting

**App won't start?**
- Make sure you ran `npm install` from both the root folder and the frontend folder
- Make sure you ran `pip install -r backend/requirements.txt`
- Check that ports 8000 and 5173 aren't being used by other programs

**Can't access Google Sheets?**
- Verify the spreadsheet URL is correct
- Make sure the spreadsheet is publicly viewable (Share → Anyone with link can view)

**Changes not showing?**
- Refresh your browser
- Press `Ctrl+C` to stop the app, then run `npm run dev` again

## Contributing to the App

If you're a developer and want to improve this app, here's how to contribute:

### Getting the Code

1. **Fork the repository** on GitHub (if this is hosted on GitHub)
   - Click the "Fork" button in the top right
   - This creates your own copy of the project

2. **Clone your fork** to your local machine:
```bash
git clone https://github.com/YOUR-USERNAME/expense-report-automation.git
cd expense-report-automation
```

3. **Add the original repository as "upstream"**:
```bash
git remote add upstream https://github.com/ORIGINAL-OWNER/expense-report-automation.git
```

### Making Changes

1. **Create a new branch** for your feature or fix:
```bash
git checkout -b feature/your-feature-name
```
   Use descriptive branch names like:
   - `feature/add-export-to-csv`
   - `fix/date-parsing-bug`
   - `docs/update-installation-guide`

2. **Make your changes** to the code

3. **Test your changes** thoroughly:
```bash
npm run dev
```
   Make sure everything works as expected

4. **Commit your changes**:
```bash
git add .
git commit -m "Brief description of what you changed"
```
   Write clear, descriptive commit messages

5. **Push to your fork**:
```bash
git push origin feature/your-feature-name
```

### Submitting a Pull Request

1. Go to your fork on GitHub
2. Click "Pull Request" or "Compare & pull request"
3. Make sure the base repository is the original and base branch is `main`
4. Write a clear description of:
   - What you changed
   - Why you changed it
   - How to test it
5. Click "Create Pull Request"

### Code Guidelines

- **Frontend**: React with TypeScript, follow existing patterns
- **Backend**: Python with FastAPI, use type hints
- **Formatting**: Keep code style consistent with existing files
- **Comments**: Add comments for complex logic
- **Testing**: Test your changes with real expense data

### Project Structure (Abridged)

- `backend/` - FastAPI Python backend
  - `api.py` - Main API endpoints
  - `models.py` - Pydantic schemas
  - `pdf_generator.py` - Affidavit PDF generation
  - `templates/` - PDF templates and fonts
    - `blank_affidavit.pdf` - Blank affidavit template
    - `fonts/` - Custom fonts for PDFs
- `frontend/src/` - React TypeScript frontend
  - `components/` - React components
    - `ExpenseForm.tsx` - Main form with two buttons
    - `ResultsView.tsx` - Reconciliation results
    - `AffidavitsModal.tsx` - Modal for generating affidavits
  - `utils/` - Utility functions
    - `parseExpenses.ts` - Frontend expense parser
  - `api.ts` - API client
  - `types.ts` - TypeScript interfaces
  - `styles/` - CSS styling
    - `App.css` - Main app styles
    - `Modal.css` - Modal styles
- `models.py` - Core data models
- `parser.py` - Google Sheets parser
- `reconcile.py` - Matching logic

### Development Tips

**Running backend only:**
```bash
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

**Running frontend only:**
```bash
cd frontend && npm run dev
```

**API documentation:**
Visit `http://localhost:8000/docs` when backend is running

### Reporting Issues

If you find a bug but don't know how to fix it:
1. Check if the issue already exists
2. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable

## License

MIT
