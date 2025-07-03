# 🔧 Port Conflict Resolution

If you encounter port conflicts, the startup script automatically handles them.

## ✅ Automatic Resolution

The `start-accessibility-tool.sh` script automatically:
1. **Scans for available ports** starting from 8001 (web) and 11434 (Ollama)
2. **Creates a .env file** with the found ports
3. **Starts services** with zero conflicts

Simply run:
```bash
./start-accessibility-tool.sh
```

## 🛠️ Manual Troubleshooting (Advanced Users Only)

If the automatic resolution doesn't work, you can manually diagnose:

### Check What's Using Ports
```bash
# Check specific ports
lsof -i :8001 -P -n
lsof -i :11434 -P -n

# Check Docker containers
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
```

### Manual Port Selection
If needed, you can manually specify ports by editing the `.env` file:
```bash
echo "WEB_PORT=8002" > .env
echo "OLLAMA_PORT=11435" >> .env
docker-compose up -d
```

### Stop Conflicting Services
```bash
# Stop our previous containers
docker-compose down

# Or stop specific containers if you know what they are
docker stop <container_name>
```