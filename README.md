# Projeto  – Sistema de HoneyPot Dinâmico com Mecanismos de Engano

## **Resumo do Projeto**

Este sistema HoneyPot em Python emula serviços falsos (SSH, FTP, HTTP) para capturar tentativas de intrusão, registrar detalhes das interações, gerar alertas automáticos, exportar logs encriptados/assinados, integrar-se opcionalmente à rede TOR e fornecer um painel de controlo web em Flask para monitorização e gestão em tempo real.

---

## **Funcionalidades Principais**

- **Emulação de Serviços:**  
  Emula SSH (porta 2222), FTP (2121) e HTTP (8080) por padrão, com possibilidade de configuração dinâmica de portas e ativação/desativação de serviços.
- **Registo Detalhado:**  
  Todas as tentativas de conexão são registadas com IP, timestamp e dados transmitidos. Os logs são encriptados (AES) e assinados digitalmente (RSA).
- **Alertas Automáticos:**  
  Geração de alertas por email para cada tentativa de conexão (configurável em `honeypot/alert.py`).
- **Exportação de Logs:**  
  Logs podem ser exportados e descarregados pelo painel web, já desencriptados e verificados.
- **Integração com TOR:**  
  Possibilidade de iniciar um nó TOR pelo painel para ocultar a origem do honeypot.
- **Painel de Controlo Web (Flask):**  
  Visualização de logs em tempo real, controlo de serviços, configuração de portas, exportação de logs e gestão do TOR.

---

## **Como Usar**

### **1. Instalação de Dependências**
No terminal, na raiz do projeto:
```bash
pip install -r requirements.txt
```

### **2. Configuração Inicial**
- Edite `honeypot/alert.py` com as credenciais do seu servidor SMTP para alertas por email.
- (Opcional) Certifique-se de que o TOR está instalado e disponível no PATH do sistema para integração TOR.

### **3. Execução**
```bash
python run.py
```

### **4. Aceder ao Painel**
Abra o navegador em: [http://localhost:5000](http://localhost:5000)

### **5. Funcionalidades do Painel**
- **Ativar/Desativar Serviços:** Marque/desmarque os serviços e altere as portas conforme necessário. Clique em “Update Configuration” e reinicie o honeypot para aplicar.
- **Exportar Logs:** Clique em “Download Logs” para descarregar os logs desencriptados.
- **TOR:** Clique em “Start TOR” para iniciar o proxy TOR e ocultar a origem do honeypot.
- **Visualizar Logs:** Veja todas as interações em tempo real na tabela de logs.

---

## **Estrutura dos Ficheiros**

```
proj_final/
│
├── honeypot/
│   ├── services/         # Emuladores de SSH, FTP, HTTP
│   ├── logger.py         # Log encriptado e assinado
│   ├── alert.py          # Alertas por email
│   ├── tor.py            # Integração com TOR
│   └── config.py         # Configuração dinâmica de serviços/portas
│
├── web/
│   ├── dashboard.py      # Painel Flask
│
├── logs/                 # Logs encriptados e exportados
│
├── requirements.txt
└── run.py                # Ponto de entrada principal
```

---

## **Notas de Segurança**

- As chaves de encriptação e assinatura são geradas automaticamente e armazenadas localmente.
- Os logs são encriptados e assinados para garantir confidencialidade e integridade.
- Recomenda-se proteger o acesso ao painel Flask em ambientes de produção.

---

## **Personalização**

- Para adicionar mais serviços, crie novos módulos em `honeypot/services/` e registre-os em `config.py`.
- Para outros canais de alerta, expanda `honeypot/alert.py`.
- Para integração total com TOR (todo o tráfego), será necessário configurar o sistema para usar o proxy SOCKS5 do TOR.

---