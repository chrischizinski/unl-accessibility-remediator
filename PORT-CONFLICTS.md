# 🔧 Fixing Port Conflicts

If you see an error like:
```
Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint... Bind for 0.0.0.0:11434 failed: port is already allocated
```

This means another program is using the same network port. Here's how to fix it:

## 🚀 Quick Fix (Recommended)

### Step 1: Stop Everything
```bash
# Stop any running accessibility tool containers
docker-compose down

# Stop all Docker containers (if needed)
docker stop $(docker ps -q)
```

### Step 2: Clean Up
```bash
# Remove any leftover containers
docker container prune -f

# Remove any leftover networks
docker network prune -f
```

### Step 3: Restart
```bash
# Start the tool again
./start-accessibility-tool.sh
```

## 🔍 Advanced: Check What's Using the Port

### On macOS/Linux:
```bash
# Check what's using port 11434 (Ollama)
lsof -i :11434

# Check what's using port 8001 (Web interface)
lsof -i :8001
```

### On Windows:
```cmd
# Check what's using port 11434
netstat -ano | findstr :11434

# Check what's using port 8001  
netstat -ano | findstr :8001
```

## 🛑 If Ollama is Already Running

If you have Ollama installed separately on your computer:

### Option 1: Use Your Existing Ollama
1. Stop the Docker version: `docker-compose down`
2. Make sure your Ollama has the right models: `ollama pull llama3.1:8b`
3. Start only the web interface:
   ```bash
   docker run -p 8001:8000 -v ./input:/app/input -v ./output:/app/output -v ./reports:/app/reports -e OLLAMA_HOST=http://host.docker.internal:11434 accessibility-remediator
   ```

### Option 2: Stop Your Existing Ollama
```bash
# Stop Ollama service
brew services stop ollama  # macOS with Homebrew
# or
sudo systemctl stop ollama  # Linux
# or
pkill ollama  # Force stop
```

Then restart the accessibility tool normally.

## 🆘 Still Having Issues?

### Nuclear Option: Reset Everything
```bash
# Stop all containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all networks
docker network prune -f

# Remove all volumes (WARNING: This removes all Docker data)
docker volume prune -f

# Restart Docker Desktop
# Then try starting the tool again
```

### Alternative Ports
If ports 8001 and 11434 are permanently occupied, you can manually edit `docker-compose.yml` to use different ports:

```yaml
services:
  ollama:
    ports:
      - "11435:11434"  # Changed from 11434 to 11435
  
  accessibility-remediator:
    ports:
      - "8002:8000"    # Changed from 8001 to 8002
```

Then access the tool at `http://localhost:8002` instead.

---

**Need more help?** Create an issue on GitHub with the exact error message you're seeing.