import psutil
import time
import os
from datetime import datetime

class MonitorSistema:
    """Monitor de recursos para otimizar uso da IA"""
    
    @staticmethod
    def verificar_compatibilidade():
        """Verifica se o sistema pode rodar os modelos"""
        mem = psutil.virtual_memory()
        cpu_cores = psutil.cpu_count()
        
        print("=" * 50)
        print("🖥️  ANÁLISE DO SISTEMA")
        print("=" * 50)
        
        # RAM
        ram_total = mem.total / (1024**3)
        ram_disponivel = mem.available / (1024**3)
        print(f"\n💾 MEMÓRIA RAM:")
        print(f"   Total: {ram_total:.1f} GB")
        print(f"   Disponível: {ram_disponivel:.1f} GB")
        print(f"   Em uso: {mem.percent}%")
        
        # Recomendações baseadas na RAM disponível
        print(f"\n🤖 MODELOS RECOMENDADOS:")
        if ram_disponivel >= 8:
            print("   ✅ Mistral 7B Q4 - Melhor qualidade")
            print("   ✅ Llama 3.2 3B - Mais rápido")
            print("   ✅ Qwen 2.5 7B Q4 - Bom em código")
        elif ram_disponivel >= 5:
            print("   ✅ Llama 3.2 3B Q4 - Recomendado")
            print("   ⚠️  Mistral 7B Q3 - Pode ser lento")
            print("   ✅ Phi-3-mini - Alternativa leve")
        elif ram_disponivel >= 3:
            print("   ✅ Llama 3.2 1B - Mais leve")
            print("   ✅ Phi-3-mini Q4 - Eficiente")
            print("   ⚠️  Modelos maiores não recomendados")
        else:
            print("   ❌ RAM insuficiente!")
            print("   💡 Feche outros programas")
        
        # CPU
        print(f"\n⚙️  PROCESSADOR:")
        print(f"   Cores: {cpu_cores}")
        print(f"   Uso atual: {psutil.cpu_percent(interval=1)}%")
        
        # Disco
        disco = psutil.disk_usage('/')
        print(f"\n💿 ARMAZENAMENTO:")
        print(f"   Livre: {disco.free / (1024**3):.1f} GB")
        print(f"   Necessário: ~10-20 GB para modelos")
        
        # Status final
        print("\n" + "=" * 50)
        if ram_disponivel >= 5:
            print("✅ SISTEMA PRONTO PARA IA LOCAL!")
        else:
            print("⚠️  SISTEMA LIMITADO - Use modelos menores")
        print("=" * 50)
        
        return ram_disponivel
    
    @staticmethod
    def monitorar_em_tempo_real(intervalo=2):
        """Monitora recursos em tempo real"""
        print("\n🔍 Monitoramento em tempo real (Ctrl+C para parar)")
        print("-" * 50)
        
        try:
            while True:
                # Limpa tela (Windows)
                os.system('cls' if os.name == 'nt' else 'clear')
                
                mem = psutil.virtual_memory()
                cpu = psutil.cpu_percent(interval=0.1)
                
                print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
                print(f"\n💾 RAM: {mem.percent}% usado")
                print(f"   Livre: {mem.available / (1024**3):.1f} GB")
                
                print(f"\n⚙️  CPU: {cpu}%")
                
                # Processos que mais consomem RAM
                print(f"\n📊 Top 5 processos (RAM):")
                processos = []
                for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                    try:
                        processos.append(proc.info)
                    except:
                        pass
                
                processos.sort(key=lambda x: x['memory_percent'], reverse=True)
                for i, proc in enumerate(processos[:5], 1):
                    print(f"   {i}. {proc['name'][:20]:20} {proc['memory_percent']:.1f}%")
                
                # Aviso se RAM baixa
                if mem.available / (1024**3) < 3:
                    print("\n⚠️  AVISO: RAM BAIXA PARA IA!")
                
                time.sleep(intervalo)
                
        except KeyboardInterrupt:
            print("\n\n✅ Monitoramento encerrado")
    
    @staticmethod
    def otimizar_sistema():
        """Dicas para otimizar o sistema"""
        print("\n💡 DICAS DE OTIMIZAÇÃO:")
        print("=" * 50)
        
        print("\n1️⃣ ANTES DE RODAR A IA:")
        print("   • Feche navegadores (Chrome/Firefox consomem muita RAM)")
        print("   • Feche IDEs pesadas (VS Code pode usar 1-2GB)")
        print("   • Desative antivírus temporariamente (se seguro)")
        print("   • Feche apps de comunicação (Discord, Slack)")
        
        print("\n2️⃣ CONFIGURAÇÕES DO MODELO:")
        print("   • Use quantização Q4_K_M ou Q3_K_S")
        print("   • Limite o contexto (num_ctx: 2048)")
        print("   • Ajuste threads (num_thread: 4)")
        print("   • Use batch pequeno (num_batch: 8)")
        
        print("\n3️⃣ ALTERNATIVAS PARA ECONOMIA:")
        print("   • Use modo offline quando possível")
        print("   • Implemente cache agressivo")
        print("   • Processe perguntas em lote")
        print("   • Use modelos menores para tarefas simples")
        
        print("\n4️⃣ COMANDOS ÚTEIS OLLAMA:")
        print("   ollama list          # Ver modelos instalados")
        print("   ollama ps            # Ver modelos rodando")
        print("   ollama stop MODEL    # Parar modelo")
        print("   ollama rm MODEL      # Remover modelo")
        
if __name__ == "__main__":
    monitor = MonitorSistema()
    
    print("🔧 VERIFICADOR DE SISTEMA PARA IA LOCAL")
    print("=" * 50)
    
    # Verifica compatibilidade
    ram_disponivel = monitor.verificar_compatibilidade()
    
    # Menu
    while True:
        print("\n📋 OPÇÕES:")
        print("1. Verificar sistema novamente")
        print("2. Monitorar em tempo real")
        print("3. Ver dicas de otimização")
        print("4. Sair")
        
        escolha = input("\nEscolha (1-4): ").strip()
        
        if escolha == '1':
            monitor.verificar_compatibilidade()
        elif escolha == '2':
            monitor.monitorar_em_tempo_real()
        elif escolha == '3':
            monitor.otimizar_sistema()
        elif escolha == '4':
            print("\n👋 Até logo!")
            break
        else:
            print("❌ Opção inválida")
