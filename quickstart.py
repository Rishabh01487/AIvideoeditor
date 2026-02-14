#!/usr/bin/env python3
"""Quick start script for AI Video Editor Platform"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and report status"""
    print(f"\n{'='*50}")
    print(f"▶ {description}")
    print(f"{'='*50}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=str(Path(__file__).parent))
        if result.returncode == 0:
            print(f"✓ {description} completed")
            return True
        else:
            print(f"✗ {description} failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Main setup function"""
    project_root = Path(__file__).parent

    print("""
    ╔════════════════════════════════════════════════════╗
    ║   AI Video Editor Platform - Quick Start         ║
    ╚════════════════════════════════════════════════════╝
    """)

    # Check Docker
    print("\n✓ Checking prerequisites...")
    result = subprocess.run("docker-compose --version", shell=True, capture_output=True)
    if result.returncode != 0:
        print("✗ Docker Compose not found. Please install Docker Desktop first.")
        sys.exit(1)
    print("✓ Docker Compose is installed")

    # Create .env if not exists
    env_file = project_root / "backend" / ".env"
    if not env_file.exists():
        print("\n✓ Creating .env file...")
        env_example = project_root / "backend" / ".env.example"
        env_file.write_text(env_example.read_text())
        print("✓ Created backend/.env")
        print("  ⚠️  Please review SECRET_KEY in backend/.env")

    # Create directories
    os.makedirs(project_root / "backend" / "ai_engine" / "assets", exist_ok=True)
    os.makedirs("/tmp/ai_video_editor", exist_ok=True)
    print("✓ Created necessary directories")

    # Start services
    if not run_command("docker-compose up -d", "Starting Docker services"):
        sys.exit(1)

    # Wait for services
    print("\n✓ Waiting for services to be ready...")
    import time
    for i in range(30):
        result = subprocess.run(
            "docker-compose exec -T postgres pg_isready -U postgres",
            shell=True,
            capture_output=True,
            cwd=str(project_root)
        )
        if result.returncode == 0:
            print("✓ PostgreSQL is ready")
            break
        time.sleep(2)

    # Initialize database
    if not run_command(
        "docker-compose exec -T backend python -c 'from app.database import init_db; init_db(); print(\"Database initialized\")'",
        "Initializing database"
    ):
        print("\n⚠️  Database initialization may have failed. You can try manually:")
        print("  docker-compose exec backend python -c 'from app.database import init_db; init_db()'")

    # Show status
    print(f"\n{'='*50}")
    print("Service Status")
    print(f"{'='*50}\n")
    subprocess.run("docker-compose ps", shell=True, cwd=str(project_root))

    # Print next steps
    print(f"""
    {'='*50}
    ✓ Setup Complete!
    {'='*50}

    Access the application at:
      • Frontend:     http://localhost:3000
      • Backend API:  http://localhost:8000
      • API Docs:     http://localhost:8000/docs
      • MinIO:        http://localhost:9001

    Next steps:
      1. Open http://localhost:3000 in your browser
      2. Register a new account
      3. Create a project and upload a video
      4. Start editing!

    For more information:
      • README.md       - Full documentation
      • DEVELOPMENT.md  - Development guide
      • CONFIG.md       - Configuration reference
      • DEPLOYMENT.md   - Production deployment

    Useful commands:
      • View logs:      docker-compose logs -f
      • Stop services:  docker-compose down
      • Reset data:     docker-compose down -v

    Optional: Enable Ollama for AI prompt parsing:
      ollama pull llama3
      ollama serve

    Happy coding! 🚀
    """)

if __name__ == "__main__":
    main()
