# **Temperature and Humidity Reporter**
**Coursera Project:** *Interface for Embedded Systems using Python and Qt* ([PDF](misc/Assignment.pdf))	

---

## ✅ **Prerequisites**
- **Python**: Version `3.10.12`
- **OS**: Ubuntu Linux `22.04`

---

## 🐍 **Virtual Environment Setup**

Create and activate a Python virtual environment to isolate dependencies:

```bash
# 1. Create the virtual environment
python3 -m venv .venv

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Install required dependencies
python3 -m pip install -r misc/requirements.txt
```

To close the venv remember use:
```sh
deactivate
```

### DB: mysqlDB

Install mysql (full guide [here](https://documentation.ubuntu.com/server/how-to/databases/install-mysql/)):

```sh
sudo apt install mysql-server
```

After install mysql, use to copy the Database:

```sh
mysql -u root -p

CREATE DATABASE sensor_data;
EXIT

mysql -u root sensor_data < misc/backup.sql
```

## How It Works

Active the **venv** and execute:

```sh
source .venv/bin/activate

python3 main.py
```

- **New Data Display:**
  - When new data arrives, it appears in the **upper-right corner** of the user interface.

- **Statistics Button:**
  - Freezes other UI elements to prevent interactions during calculation.
  - Collects *N* samples (the parameter is defined in [DataProcessed.py](DataProcessed.py)).
  - Displays calculated statistics once the required number of samples is reached.

- **Graphic Button:**
  - Similar behavior to the Statistics button but for plotting graphs.
  - Blocks other UI actions until the process is complete.

- **Threshold (Alarm):**
  - Only works when a plot is visible on the screen.
  - If a sensor value exceeds the defined threshold, the marker color changes as a visual alert.


Enjoy!!
