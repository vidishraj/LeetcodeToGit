# 🚀 LeetCode Git Sync

## 📌 About

LeetCode Git Sync is a powerful tool designed to **automate the saving of your best LeetCode solutions** to a **local or remote Git repository**. Never lose your well-crafted solutions again! This tool fetches your submissions directly from LeetCode, commits them to a Git repository, and even pushes them to a remote repo if specified.

---

## 🎯 Features

- 📂 **Sync your best LeetCode solutions** to a Git repository
- 🔄 **Automatic fetching** of solved problems based on difficulty
- 🔍 **Commits solutions automatically** with detailed metadata
- ☁️ **Pushes to a remote Git repo** (optional)
- 🛠 **Handles errors gracefully** and even rolls back failed pushes

---

## 🛠 Installation & Setup

### 1️⃣ Clone the Repository

```sh
 git clone <repo_url>
 cd leetcode-git-sync
```

### 2️⃣ Install Dependencies

```sh
 pip install -r requirements.txt
```

### 3️⃣ Add Your LeetCode Cookies 🍪

- Open any **network request** to `www.leetcode.com/graphql` in your browser's DevTools after logging in
- Copy your cookies
- Paste them into `leetcode_cookies.txt`

---

## 🚀 How It Works

The script runs in **four stages**:

### 🔹 **Stage 1: Initialization**

- 🏗 **Creates a local Git repository**
- 🔗 **Adds remote URL** (if provided)
- ✅ **Checks LeetCode connection** (using cookies)
- 🔍 **Verifies push permissions**

### 🔹 **Stage 2: Fetching Solutions**

- 📌 Fetches **all solved problems** based on selected difficulties
- 📤 Retrieves **best submissions** for each problem
- ⚠️ Skips already existing solutions

### 🔹 **Stage 3: Committing to Git**

- 💾 Fetches **actual code** from LeetCode submissions
- 📜 Commits code to **local repository**
- 📑 Updates **README summary**

### 🔹 **Stage 4: Pushing to Remote**

- 🚀 Pushes commits to **remote repository**
- 🔄 Rolls back failed pushes (if `--deleteIfFail` is enabled)

---

## ⚡ Usage

Run the script with various command-line flags:

```sh
python main.py --difficulty emh --remote https://github.com/user/leetcode-solutions.git --gittoken YOUR_GIT_TOKEN
```

### 🏷 Available Flags

| Flag             | Required | Description                                       |
| ---------------- | -------- | ------------------------------------------------- |
| `--remote`       | ❌        | Specifies the remote repository URL               |
| `--localName`    | ❌        | Name of the local Git repository                  |
| `--gittoken`     | ❌        | Git token for authentication (if needed)          |
| `--difficulty`   | ✅        | Combination of `e`, `m`, `h` (Easy, Medium, Hard) |
| `--deleteIfFail` | ❌        | Rolls back commits if remote push fails           |

---

## 🎯 Example Scenarios

### 1️⃣ Save **Easy & Medium** problems to a local repo

```sh
python main.py --difficulty em --localName MyLeetCodeRepo
```

### 2️⃣ Save **Hard** problems & push to a GitHub repo

```sh
python main.py --difficulty h --remote https://github.com/user/leetcode-solutions.git
```

### 3️⃣ Save **All** problems & push using a Git token

```sh
python main.py --difficulty emh --remote https://github.com/user/leetcode-solutions.git --gittoken ghp_1234567890
```

---

## 📢 Contributing

Want to improve LeetCode Git Sync? Feel free to fork the repo, create a branch, and submit a PR! Contributions are always welcome. 🚀

---

## 📜 License

This project is licensed under the MIT License.

---

💡 **Happy Coding! **&#x20;
