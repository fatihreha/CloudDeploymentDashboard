#!/usr/bin/env python3
"""Test Docker client connection"""

import docker

try:
    print("Testing Docker client connection...")
    client = docker.from_env()
    print("✅ Docker client connected successfully")
    
    # Get all containers
    containers = client.containers.list(all=True)
    print(f"✅ Found {len(containers)} total containers")
    
    # Get running containers
    running_containers = client.containers.list()
    print(f"✅ Found {len(running_containers)} running containers")
    
    # Show first 5 containers
    print("\n📋 First 5 containers:")
    for i, container in enumerate(containers[:5]):
        print(f"  {i+1}. {container.name}: {container.status}")
        
except docker.errors.DockerException as e:
    print(f"❌ Docker connection error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")