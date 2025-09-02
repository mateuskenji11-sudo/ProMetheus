# assistente_local.py
import ollama
import json
import time
import psutil
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pickle
import os

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AssistenteAcademicoCristao:
    """
    Assistente IA local com valores cristãos para auxílio acadêmico
    Otimizado para rodar com 10GB RAM
    """
    
    def __init__(self, modelo="llama3.2:3b-instruct-q4_K_M", max_ram_gb=10):
        self.modelo = modelo
        self.max_ram_gb = max_ram_gb
        self.historico = []
        self.cache_respostas = {}
        self.contexto_cristao = self._carregar_contexto_cristao()
        self.verificar_recursos()
        
    def _carregar_contexto_cristao(self) -> str:
        """Carrega o contexto base com valores cristãos"""
        return """
        Você é um assistente acadêmico guiado por princípios cristãos.
        
        Diretrizes fundamentais:
        1. Sempre seja honesto, paciente e compassivo
        2. Promova o conhecimento de forma ética e construtiva
        3. Ajude com excelência, como em Colossenses 3:23
        4. Seja humilde e reconheça limitações quando necessário
        5. Evite conteúdo inadequado ou prejudicial
        
        Especialidades:
        - Programação (Python, JavaScript, C++, etc.)
        - Ciência da Computação
        - Matemática e Algoritmos
        - Desenvolvimento de Software
        - Inteligência Artificial
        
        Responda sempre em português brasileiro, de forma clara e didática.
        """
    
    def verificar_recursos(self) -> Dict:
        """Verifica recursos do sistema"""
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        
        status = {
            'ram_disponivel_gb': mem.available / (1024**3),
            'ram_usada_pct': mem.percent,
            'cpu_uso_pct': cpu,
            'pode_executar': mem.available / (1024**3) >= 3
        }
        
        if not status['pode_executar']:
            logging.warning(f"⚠️ RAM baixa: {status['ram_disponivel_gb']:.1f}GB disponível")
        else:
            logging.info(f"✅ Sistema OK: {status['ram_disponivel_gb']:.1f}GB RAM disponível")
            
        return status
    
    def otimizar_prompt(self, pergunta: str, contexto_aula: str = "") -> str:
        """Otimiza o prompt para melhor resposta"""
        prompt_completo = f"{self.contexto_cristao}\n"
        
        if contexto_aula:
            prompt_completo += f"\nContexto da aula:\n{contexto_aula}\n"
        
        # Adiciona histórico relevante (últimas 3 interações)
        if self.historico:
            prompt_completo += "\nHistórico recente:\n"
            for h in self.historico[-3:]:
                prompt_completo += f"P: {h['pergunta'][:100]}...\n"
                prompt_completo += f"R: {h['resposta'][:100]}...\n\n"
        
        prompt_completo += f"\nPergunta atual: {pergunta}"
        
        return prompt_completo
    
    def responder(self, 
                  pergunta: str, 
                  contexto_aula: str = "",
                  modo_offline: bool = False,
                  usar_cache: bool = True) -> str:
        """
        Gera resposta para a pergunta
        
        Args:
            pergunta: Pergunta do usuário
            contexto_aula: Contexto adicional da aula
            modo_offline: Se True, usa apenas cache
            usar_cache: Se True, verifica cache antes de gerar
        """
        
        # Verifica cache
        cache_key = f"{pergunta}_{contexto_aula}"
        if usar_cache and cache_key in self.cache_respostas:
            logging.info("📚 Resposta do cache")
            return self.cache_respostas[cache_key]
        
        if modo_offline:
            return self._buscar_resposta_similar(pergunta)
        
        # Verifica recursos antes de processar
        status = self.verificar_recursos()
        if not status['pode_executar']:
            return "⚠️ Sistema com poucos recursos. Tente uma pergunta mais simples."
        
        try:
            # Prepara o prompt otimizado
            prompt = self.otimizar_prompt(pergunta, contexto_aula)
            
            # Gera resposta
            inicio = time.time()
            
            resposta = ollama.chat(
                model=self.modelo,
                messages=[
                    {'role': 'system', 'content': self.contexto_cristao},
                    {'role': 'user', 'content': pergunta}
                ],
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'num_ctx': 2048,  # Contexto reduzido para economizar RAM
                    'num_thread': 4    # Ajuste conforme seus cores
                }
            )
            
            tempo_resposta = time.time() - inicio
            texto_resposta = resposta['message']['content']
            
            # Salva no histórico e cache
            self.historico.append({
                'timestamp': datetime.now(),
                'pergunta': pergunta,
                'resposta': texto_resposta,
                'tempo_segundos': tempo_resposta
            })
            
            if usar_cache:
                self.cache_respostas[cache_key] = texto_resposta
                self._salvar_cache()
            
            logging.info(f"✅ Resposta gerada em {tempo_resposta:.1f}s")
            
            return texto_resposta
            
        except Exception as e:
            logging.error(f"❌ Erro ao gerar resposta: {e}")
            return self._resposta_erro(str(e))
    
    def _buscar_resposta_similar(self, pergunta: str) -> str:
        """Busca resposta similar no histórico (modo offline)"""
        if not self.historico:
            return "📵 Modo offline: Sem respostas no histórico. Conecte-se para gerar novas respostas."
        
        # Busca simples por palavras-chave
        palavras = pergunta.lower().split()
        melhor_match = None
        melhor_score = 0
        
        for item in self.historico:
            score = sum(1 for p in palavras if p in item['pergunta'].lower())
            if score > melhor_score:
                melhor_score = score
                melhor_match = item
        
        if melhor_match and melhor_score > 0:
            return f"📚 (Do histórico) {melhor_match['resposta']}"
        
        return "📵 Modo offline: Nenhuma resposta similar encontrada no histórico."
    
    def _resposta_erro(self, erro: str) -> str:
        """Gera resposta padrão para erros"""
        respostas_erro = {
            'connection': "🔌 Erro de conexão. Verifique se o Ollama está rodando.",
            'memory': "💾 Memória insuficiente. Feche alguns programas.",
            'model': "🤖 Modelo não encontrado. Execute: ollama pull llama3.2:3b"
        }
        
        for key, msg in respostas_erro.items():
            if key in erro.lower():
                return msg
        
        return f"❌ Erro inesperado. Verifique os logs para mais detalhes."
    
    def adicionar_conhecimento_personalizado(self, arquivo_json: str):
        """Adiciona conhecimento personalizado de um arquivo JSON"""
        try:
            with open(arquivo_json, 'r', encoding='utf-8') as f:
                conhecimento = json.load(f)
            
            for item in conhecimento:
                self.cache_respostas[item['pergunta']] = item['resposta']
            
            self._salvar_cache()
            logging.info(f"✅ {len(conhecimento)} itens adicionados ao conhecimento")
            
        except Exception as e:
            logging.error(f"❌ Erro ao carregar conhecimento: {e}")
    
    def _salvar_cache(self):
        """Salva cache em disco"""
        try:
            with open('cache_respostas.pkl', 'wb') as f:
                pickle.dump(self.cache_respostas, f)
        except Exception as e:
            logging.error(f"Erro ao salvar cache: {e}")
    
    def carregar_cache(self):
        """Carrega cache do disco"""
        try:
            if os.path.exists('cache_respostas.pkl'):
                with open('cache_respostas.pkl', 'rb') as f:
                    self.cache_respostas = pickle.load(f)
                logging.info(f"✅ Cache carregado: {len(self.cache_respostas)} respostas")
        except Exception as e:
            logging.error(f"Erro ao carregar cache: {e}")
    
    def modo_estudo(self, topico: str, num_questoes: int = 5) -> List[str]:
        """Gera questões de estudo sobre um tópico"""
        prompt = f"""
        Crie {num_questoes} questões de estudo sobre {topico}.
        Formate como:
        1. [Pergunta]
        2. [Pergunta]
        ...
        
        Foque em questões práticas e conceituais para programação.
        """
        
        resposta = self.responder(prompt)
        questoes = resposta.split('\n')
        return [q for q in questoes if q.strip()]
    
    def exportar_historico(self, arquivo: str = "historico_conversas.json"):
        """Exporta histórico de conversas"""
        try:
            historico_export = []
            for item in self.historico:
                historico_export.append({
                    'timestamp': item['timestamp'].isoformat(),
                    'pergunta': item['pergunta'],
                    'resposta': item['resposta'],
                    'tempo_segundos': item.get('tempo_segundos', 0)
                })
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(historico_export, f, ensure_ascii=False, indent=2)
            
            logging.info(f"✅ Histórico exportado: {arquivo}")
            
        except Exception as e:
            logging.error(f"❌ Erro ao exportar: {e}")
    
    def estatisticas_uso(self) -> Dict:
        """Retorna estatísticas de uso"""
        if not self.historico:
            return {'mensagem': 'Sem dados de uso ainda'}
        
        tempos = [h.get('tempo_segundos', 0) for h in self.historico]
        
        return {
            'total_perguntas': len(self.historico),
            'tempo_medio_resposta': sum(tempos) / len(tempos) if tempos else 0,
            'cache_size': len(self.cache_respostas),
            'primeira_pergunta': self.historico[0]['timestamp'].isoformat(),
            'ultima_pergunta': self.historico[-1]['timestamp'].isoformat()
        }


# ============= EXEMPLO DE USO =============

if __name__ == "__main__":
    print("🤖 Iniciando Assistente Acadêmico Cristão...")
    print("=" * 50)
    
    # Inicializa o assistente
    assistente = AssistenteAcademicoCristao()
    assistente.carregar_cache()
    
    print("\n💡 Comandos especiais:")
    print("  /offline - Modo offline (usa apenas cache)")
    print("  /stats   - Estatísticas de uso")
    print("  /export  - Exportar histórico")
    print("  /estudo [tópico] - Gerar questões de estudo")
    print("  /sair    - Encerrar")
    print("=" * 50)
    
    modo_offline = False
    
    while True:
        try:
            pergunta = input("\n📝 Sua pergunta: ").strip()
            
            if not pergunta:
                continue
            
            # Comandos especiais
            if pergunta.lower() == '/sair':
                print("👋 Até logo! Que Deus abençoe seus estudos!")
                break
            
            elif pergunta.lower() == '/offline':
                modo_offline = not modo_offline
                print(f"📵 Modo offline: {'ATIVADO' if modo_offline else 'DESATIVADO'}")
                continue
            
            elif pergunta.lower() == '/stats':
                stats = assistente.estatisticas_uso()
                print("\n📊 Estatísticas:")
                for k, v in stats.items():
                    print(f"  {k}: {v}")
                continue
            
            elif pergunta.lower() == '/export':
                assistente.exportar_historico()
                continue
            
            elif pergunta.lower().startswith('/estudo'):
                topico = pergunta.replace('/estudo', '').strip()
                if topico:
                    print(f"\n📚 Gerando questões sobre {topico}...")
                    questoes = assistente.modo_estudo(topico)
                    for q in questoes:
                        print(q)
                else:
                    print("Use: /estudo [tópico]")
                continue
            
            # Resposta normal
            print("\n🤔 Processando...")
            resposta = assistente.responder(
                pergunta, 
                modo_offline=modo_offline
            )
            
            print("\n🤖 Assistente:")
            print(resposta)
            
        except KeyboardInterrupt:
            print("\n\n👋 Programa interrompido. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            continue
    
    # Salva estatísticas ao sair
    assistente.exportar_historico()
    print(f"\n📊 Total de interações: {len(assistente.historico)}")
