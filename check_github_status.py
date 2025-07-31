#!/usr/bin/env python3
"""
GitHub Actions Status Checker
Monitor del estado de los workflows de GitHub Actions
"""
import subprocess
import json
import time
import sys

def check_github_cli():
    """Verifica si GitHub CLI está instalado"""
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ GitHub CLI está instalado")
            return True
        else:
            print("❌ GitHub CLI no está instalado")
            return False
    except FileNotFoundError:
        print("❌ GitHub CLI no encontrado")
        return False

def get_workflow_runs():
    """Obtiene los últimos workflow runs"""
    try:
        result = subprocess.run([
            'gh', 'run', 'list', 
            '--workflow=build-release.yml',
            '--limit=5',
            '--json=status,conclusion,createdAt,displayTitle,url'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error obteniendo workflows: {result.stderr}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_latest_release():
    """Obtiene información del último release"""
    try:
        result = subprocess.run([
            'gh', 'release', 'list',
            '--limit=1',
            '--json=tagName,name,createdAt,url,assets'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            releases = json.loads(result.stdout)
            return releases[0] if releases else None
        else:
            print(f"Error obteniendo releases: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def print_workflow_status(runs):
    """Imprime el estado de los workflows"""
    if not runs:
        print("🔍 No se encontraron workflows recientes")
        return
    
    print("\n📊 Últimos Workflow Runs:")
    print("-" * 60)
    
    for i, run in enumerate(runs, 1):
        status = run.get('status', 'unknown')
        conclusion = run.get('conclusion', 'N/A')
        title = run.get('displayTitle', 'Sin título')
        created = run.get('createdAt', 'Fecha desconocida')
        url = run.get('url', '')
        
        # Iconos según el estado
        if status == 'completed':
            if conclusion == 'success':
                icon = "✅"
            elif conclusion == 'failure':
                icon = "❌"
            elif conclusion == 'cancelled':
                icon = "⚠️"
            else:
                icon = "❓"
        elif status == 'in_progress':
            icon = "🔄"
        elif status == 'queued':
            icon = "⏳"
        else:
            icon = "❓"
        
        print(f"{i}. {icon} {status.upper()}")
        print(f"   Resultado: {conclusion}")
        print(f"   Título: {title}")
        print(f"   Creado: {created}")
        print(f"   URL: {url}")
        print()

def print_release_info(release):
    """Imprime información del release"""
    if not release:
        print("🔍 No se encontraron releases")
        return
    
    print("🚀 Último Release:")
    print("-" * 30)
    print(f"Tag: {release.get('tagName', 'N/A')}")
    print(f"Nombre: {release.get('name', 'N/A')}")
    print(f"Creado: {release.get('createdAt', 'N/A')}")
    print(f"URL: {release.get('url', 'N/A')}")
    
    assets = release.get('assets', [])
    if assets:
        print(f"Assets ({len(assets)}):")
        for asset in assets:
            name = asset.get('name', 'Sin nombre')
            size = asset.get('size', 0)
            size_mb = round(size / (1024*1024), 1) if size > 0 else 0
            print(f"  📎 {name} ({size_mb} MB)")
    else:
        print("  Sin assets")

def main():
    """Función principal"""
    print("🔍 GitHub Actions Status Checker")
    print("=" * 40)
    
    # Verificar GitHub CLI
    if not check_github_cli():
        print("\n💡 Para instalar GitHub CLI:")
        print("   macOS: brew install gh")
        print("   Windows: winget install GitHub.cli")
        print("   Luego autentica: gh auth login")
        return 1
    
    # Obtener información
    print("\n🔄 Obteniendo información de GitHub...")
    
    runs = get_workflow_runs()
    release = get_latest_release()
    
    # Mostrar resultados
    print_workflow_status(runs)
    print_release_info(release)
    
    # Información adicional
    print("\n💡 Comandos útiles:")
    print("   Ver workflows:    gh run list")
    print("   Ver logs:         gh run view --log")
    print("   Ver releases:     gh release list")
    print("   Manual trigger:   gh workflow run build-release.yml")
    
    # Verificar si hay runs en progreso
    if runs:
        latest_run = runs[0]
        if latest_run.get('status') == 'in_progress':
            print(f"\n🔄 Workflow en progreso: {latest_run.get('url')}")
            print("   Puedes seguir el progreso en GitHub o con: gh run watch")
        elif latest_run.get('status') == 'completed':
            if latest_run.get('conclusion') == 'success':
                print("\n🎉 ¡Último workflow completado exitosamente!")
            else:
                print(f"\n❌ Último workflow falló: {latest_run.get('conclusion')}")
                print("   Revisa los logs con: gh run view --log")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
