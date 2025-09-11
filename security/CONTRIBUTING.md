# 🛡️ Security Assessment and Vulnerability Detection Team GitHub Workflow Guide (Last updated on 6 Sept)
This guide will provide you with the steps to get started to contribute to the Evidence Collector and Validator scanner as a team

## 📂 Repository Model
- Default branch: `main`
- day-to-work work: respective feature branches from `main`  
- all changes have to submitted via Pull Requests 

## 🚀 Getting Started
**Step 1**: Fork the repository to your own GitHub account from: https://github.com/Hardhat-Enterprises/AutoAudit
- Click Fork >> Create a new fork

**Step 2**: Clone your fork into VSC 
- Option 1: Use the terminal and type (please note to change to your own github username and clone it to your preferred directory):
```
git clone https://github.com/<yourgithubusername>/AutoAudit.git
```
- Option 2: Click “Command Palette” >> type “Git: Clone” >> insert your repository (please note to change to your own github username): https://github.com/<yourgithubusername>/AutoAudit.git

Remember to access to your cloned repository before doing anything else: 
```
cd AutoAudit
```

**Step 3**: Set the original repo as upstream i.e. this is to ensure that it can be easily synced to the repository using the terminal:
```
git remote add upstream https://github.com/Hardhat-Enterprises/AutoAudit.git
git fetch upstream
```

## 🛠️ Working on a New Feature
**Step 1**: Remember to create your new task on the planner before proceeding

**Step 2**: When starting on a new task, always create a new dedicated branch. This is to ensure multiple members are able to work on their tasks concurrently without affecting the overall codebase. It is ideal for the name of the branch to be related to the task e.g. task: developing application control detection logic, the branch name shall be applicationcontrol. The steps to take to create a new branch can be found below with nameofbranch being the proposed branch name:

- Good practice to check the branch you are on which should be dev branch: 
```
git branch
```
- If not on the dev branch, switch to it: 
```
git checkout dev
```
- Sync your local develop branch with the latest changes: 
```
git fetch upstream
git pull --rebase upstream dev
git push
```
- Create new git branch and switch to the new branch:
```
git checkout -b feature/security-nameofbranch
```
- Good practice to check the branch and confirm that you are on the newly created one (it should be highlighted in green): 
```
git branch
```

**Step 3**: Once the development has been completed, commit the changes with a concise and clear description on what has been changed i.e. whathaschanged in the example:

- Adding all the changes: 
```
git add . 
```
- Or if you prefer only the specific file: 
```
git add nameoffile
```
- Committing the changes with description: 
```
git commit -m "whathaschanged"
```
- Pushing to the branch: 
```
git push origin feature/nameofbranch
```

## 🔃 Pull Request
Once the task has been completed, create a pull request on GitHub to ensure that the code is aligned with the overall tool with the following steps:

**Step 1**: Sync the local branch with upstream main to ensure that your branch is up to date with the latest changes from any other team members: 
```
git fetch upstream
```

**Step 2**: Merge upstream into your working branch – if there are any conflicts, you will need to resolve them and run git commit: 
```
git merge upstream
```

**Step 3**: Push your updated branch to the main branch: 
```
git push origin feature/nameofbranch
```

**Step 4**: Access the team’s GitHub and click on “Pull Requests” >> click on “New pull request” >> choose “compare across forks” >> select the respective repository and branch for comparison i.e. branch should be the one you just worked on and just want pull to main >> click “Create pull request” and update the fields:

- Title: Aligned to your planner’s title with PR serial (i.e. PR-SXX >> for example the first PR of the Security team will be PR-S01)
- Description should be about the changes made with ideally a screenshot or video to show what has been done – this will be useful for the code reviewer to understand the changes (and definitely useful as part of your evidence for OnTrack submission when you share the pull request link)

# 🧩 Post-PR Merge or Mid-way Work

- Always make sure your local dev branch is updated to the latest changes before any development:
```
git checkout dev
git pull upstream dev
```

- or if you are working midway on a branch and want to update with the latest changes made by the team:
```
git checkout feature/nameofbranch
git rebase dev
```

For more visual notes: visit the document guide on https://deakin365.sharepoint.com/:b:/r/sites/HardhatEnterprises2/Shared%20Documents/%F0%9F%94%92%20AutoAudit/T2%202025/Documents/Security%20Assessment%20%26%20Vulnerability%20Team/AutoAudit%20-%20Security%20Team%20GitHub%20Repo%20Workflow%20Guide.pdf?csf=1&web=1&e=jfJGAE 