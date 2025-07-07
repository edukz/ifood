import logging
import os
from datetime import datetime
from pathlib import Path
from src.config.settings import SETTINGS
from src.utils.colors import Colors, ColorPrinter


# Cache global de loggers para evitar múltiplos arquivos
_loggers_cache = {}
_log_file_handler = None
_current_log_file = None


def get_log_filename():
    """Retorna o nome do arquivo de log para o dia atual"""
    today = datetime.now().strftime('%Y%m%d')
    return f"{SETTINGS.log_dir}/ifood_scraper_{today}.log"


def setup_file_handler():
    """Configura o handler de arquivo único para todos os loggers"""
    global _log_file_handler, _current_log_file
    
    # Cria diretório de logs se não existir
    os.makedirs(SETTINGS.log_dir, exist_ok=True)
    
    # Nome do arquivo de log do dia
    log_filename = get_log_filename()
    
    # Se já temos um handler para o arquivo atual, retorna ele
    if _log_file_handler and _current_log_file == log_filename:
        return _log_file_handler
    
    # Se o handler é para um arquivo diferente (novo dia), fecha o antigo
    if _log_file_handler and _current_log_file != log_filename:
        _log_file_handler.close()
    
    # Cria novo handler
    _log_file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    _log_file_handler.setLevel(logging.DEBUG)
    
    # Formatter detalhado para arquivo
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    _log_file_handler.setFormatter(file_formatter)
    
    _current_log_file = log_filename
    return _log_file_handler


class ColoredFormatter(logging.Formatter):
    """Formatter customizado com cores"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cp = ColorPrinter()
    
    def format(self, record):
        # Salva o levelname original
        levelname_orig = record.levelname
        
        # Aplica cores baseado no nível
        if record.levelname == 'DEBUG':
            record.levelname = self.cp.dim(f"[{record.levelname}]")
        elif record.levelname == 'INFO':
            record.levelname = self.cp.info(f"[{record.levelname}]", bold=True)
        elif record.levelname == 'WARNING':
            record.levelname = self.cp.warning(f"[{record.levelname}]", bold=True)
        elif record.levelname == 'ERROR':
            record.levelname = self.cp.error(f"[{record.levelname}]", bold=True)
        elif record.levelname == 'CRITICAL':
            record.levelname = self.cp.error(f"[CRITICAL]", bold=True)
        
        # Formata o nome do logger
        record.name = self.cp.highlight(record.name)
        
        # Formata a mensagem
        formatted = super().format(record)
        
        # Restaura o levelname original
        record.levelname = levelname_orig
        
        return formatted


def setup_logger(name: str = "ifood_scraper") -> logging.Logger:
    """
    Configura e retorna um logger personalizado.
    Todos os loggers compartilham o mesmo arquivo de log.
    """
    
    # Se já existe no cache, retorna
    if name in _loggers_cache:
        return _loggers_cache[name]
    
    # Cria novo logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Remove handlers existentes para evitar duplicação
    logger.handlers = []
    
    # Console handler (compartilhado)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter colorido para console
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Força encoding UTF-8 no Windows
    import sys
    if sys.platform == 'win32':
        if hasattr(console_handler.stream, 'isatty') and console_handler.stream.isatty():
            try:
                console_handler.stream.reconfigure(encoding='utf-8')
            except:
                pass
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (compartilhado entre todos os loggers)
    file_handler = setup_file_handler()
    logger.addHandler(file_handler)
    
    # Adiciona ao cache
    _loggers_cache[name] = logger
    
    # Log de inicialização apenas uma vez por execução
    if name == "ifood_scraper" or len(_loggers_cache) == 1:
        logger.info("=" * 60)
        logger.info(f"iFood Scraper - Sessão iniciada")
        logger.info(f"Log file: {_current_log_file}")
        logger.info("=" * 60)
    
    return logger


def cleanup_old_logs(days_to_keep: int = 7):
    """
    Remove logs antigos para evitar acúmulo excessivo.
    Mantém apenas os logs dos últimos 'days_to_keep' dias.
    """
    try:
        log_dir = Path(SETTINGS.log_dir)
        if not log_dir.exists():
            return
        
        # Data limite
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        # Lista todos os arquivos de log
        for log_file in log_dir.glob("*.log"):
            # Verifica idade do arquivo
            if log_file.stat().st_mtime < cutoff_date:
                log_file.unlink()
                print(f"Log antigo removido: {log_file.name}")
                
    except Exception as e:
        print(f"Erro ao limpar logs antigos: {e}")


def get_current_log_file():
    """Retorna o caminho do arquivo de log atual"""
    return _current_log_file or get_log_filename()


def close_all_loggers():
    """Fecha todos os handlers de arquivo (útil para testes)"""
    global _log_file_handler
    
    if _log_file_handler:
        _log_file_handler.close()
        _log_file_handler = None
    
    # Limpa o cache
    _loggers_cache.clear()