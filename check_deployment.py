"""
Script para verificar que el proyecto está listo para desplegar
"""
import os
import sys
from pathlib import Path

def check_files():
    """Verifica que existan todos los archivos necesarios"""
    required_files = [
        'requirements-streamlit.txt',
        'src/dashboard/multi_sport_app.py',
        'models/nba_predictor.joblib',
        'data/nba_games_features.parquet',
        '.gitignore',
        'README.md'
    ]
    
    print("🔍 Verificando archivos necesarios...\n")
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / (1024 * 1024)  # MB
            print(f"✅ {file} ({size:.2f} MB)")
        else:
            print(f"❌ {file} - NO ENCONTRADO")
            missing.append(file)
    
    return missing

def check_file_sizes():
    """Verifica el tamaño de archivos (GitHub tiene límite de 100MB)"""
    print("\n📦 Verificando tamaños de archivos...\n")
    
    large_files = []
    for root, dirs, files in os.walk('.'):
        # Ignorar .venv, __pycache__, etc
        dirs[:] = [d for d in dirs if d not in ['.venv', 'venv', '__pycache__', '.git', 'Analisis1']]
        
        for file in files:
            filepath = os.path.join(root, file)
            try:
                size = os.path.getsize(filepath) / (1024 * 1024)  # MB
                if size > 50:  # Archivos mayores a 50MB
                    large_files.append((filepath, size))
            except:
                pass
    
    if large_files:
        print("⚠️  Archivos grandes detectados (pueden causar problemas en GitHub):\n")
        for file, size in sorted(large_files, key=lambda x: x[1], reverse=True):
            print(f"   📁 {file}: {size:.2f} MB")
        print("\n💡 Considera usar Git LFS o cargar desde URL para archivos > 100MB")
    else:
        print("✅ Todos los archivos tienen tamaño adecuado para GitHub")
    
    return large_files

def check_imports():
    """Verifica que las importaciones del dashboard funcionen"""
    print("\n🐍 Verificando importaciones de Python...\n")
    
    try:
        sys.path.insert(0, os.getcwd())
        
        # Intentar importar las librerías principales
        imports = [
            ('streamlit', 'Streamlit'),
            ('pandas', 'Pandas'),
            ('numpy', 'NumPy'),
            ('plotly', 'Plotly'),
            ('sklearn', 'Scikit-learn'),
            ('joblib', 'Joblib')
        ]
        
        failed = []
        for module, name in imports:
            try:
                __import__(module)
                print(f"✅ {name}")
            except ImportError:
                print(f"❌ {name} - NO INSTALADO")
                failed.append(name)
        
        return failed
    except Exception as e:
        print(f"❌ Error al verificar importaciones: {e}")
        return []

def check_env():
    """Verifica variables de entorno"""
    print("\n🔑 Verificando configuración...\n")
    
    if os.path.exists('.env'):
        print("✅ Archivo .env encontrado")
        
        # Verificar .env.example
        if os.path.exists('.env.example'):
            print("✅ Archivo .env.example encontrado")
        else:
            print("⚠️  .env.example no encontrado (recomendado para usuarios)")
    else:
        print("⚠️  Archivo .env no encontrado (opcional para desarrollo local)")
    
    # Verificar gitignore
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            content = f.read()
            if '.env' in content:
                print("✅ .env está en .gitignore (seguro)")
            else:
                print("⚠️  .env NO está en .gitignore (¡añádelo!)")

def generate_report():
    """Genera reporte completo"""
    print("=" * 60)
    print("🚀 VERIFICACIÓN DE DESPLIEGUE - Sistema Multi-Deporte")
    print("=" * 60)
    
    missing_files = check_files()
    large_files = check_file_sizes()
    failed_imports = check_imports()
    check_env()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    
    ready = True
    
    if missing_files:
        print(f"\n❌ Faltan {len(missing_files)} archivos necesarios")
        ready = False
    else:
        print("\n✅ Todos los archivos necesarios están presentes")
    
    if large_files:
        total_size = sum(size for _, size in large_files)
        print(f"\n⚠️  {len(large_files)} archivos grandes detectados ({total_size:.2f} MB total)")
        if any(size > 100 for _, size in large_files):
            print("   ⚠️  Algunos archivos > 100MB (GitHub los rechazará)")
            ready = False
    
    if failed_imports:
        print(f"\n❌ Faltan {len(failed_imports)} librerías: {', '.join(failed_imports)}")
        print("   💡 Instala con: pip install -r requirements-streamlit.txt")
        ready = False
    else:
        print("\n✅ Todas las librerías necesarias están instaladas")
    
    print("\n" + "=" * 60)
    
    if ready:
        print("🎉 ¡LISTO PARA DESPLEGAR!")
        print("\n📝 Siguiente paso:")
        print("   1. Lee QUICKSTART_DEPLOY.md")
        print("   2. Sube a GitHub: git add . && git commit -m 'Ready' && git push")
        print("   3. Despliega en Streamlit Cloud: https://share.streamlit.io/")
    else:
        print("⚠️  HAY PROBLEMAS QUE RESOLVER")
        print("\n📝 Acciones recomendadas:")
        if missing_files:
            print("   • Generar archivos faltantes")
        if large_files:
            print("   • Configurar Git LFS o usar URLs para archivos grandes")
        if failed_imports:
            print("   • Instalar librerías faltantes")
    
    print("=" * 60)

if __name__ == "__main__":
    generate_report()
