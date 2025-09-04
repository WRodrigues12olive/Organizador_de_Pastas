📂 Organizador de Arquivos Automático com PySide6
Uma aplicação de desktop desenvolvida em Python e PySide6 para organizar arquivos automaticamente em pastas com base em suas extensões, tudo através de uma interface gráfica bonita e intuitiva.

<img width="995" height="783" alt="image" src="https://github.com/user-attachments/assets/68b76d2d-c559-4cc3-9c08-eb480698dfe3" />


📖 Sobre o Projeto
Este projeto foi criado para resolver um problema comum: pastas de "Downloads" (ou qualquer outra) que se tornam caóticas e desorganizadas com o tempo. Em vez de organizar arquivos manualmente, esta aplicação monitora uma pasta de sua escolha e move os arquivos para subpastas categorizadas com base em regras que você mesmo define.

A interface foi construída com PySide6 para ser moderna e fácil de usar, e a lógica de monitoramento roda em uma thread separada para garantir que a aplicação permaneça responsiva o tempo todo.

✨ Funcionalidades
Interface Gráfica Intuitiva: Um design limpo e moderno com tema escuro.

Seleção de Pasta Dinâmica: Escolha qualquer pasta em seu computador para organizar.

Gerenciamento de Regras Customizável: Adicione, edite e remova categorias (ex: "Imagens") e as extensões de arquivo correspondentes (ex: .jpg, .png).

Monitoramento em Segundo Plano: O processo de organização roda em uma thread separada, não travando a interface.

Log de Atividades em Tempo Real: Acompanhe quais arquivos estão sendo movidos.

Persistência de Configurações: Suas regras e a última pasta selecionada são salvas em um arquivo organizador_config.json, para que você não precise reconfigurar tudo a cada vez que abre o app.

🛠️ Tecnologias Utilizadas
Python 3: Linguagem principal do projeto.

PySide6: Biblioteca para a criação da interface gráfica (bindings oficiais do Qt para Python).

qtawesome: Para a inclusão de ícones modernos na interface.

🚀 Como Executar o Projeto
Siga os passos abaixo para executar a aplicação em sua máquina local.

Pré-requisitos
Python 3.8 ou superior

pip (gerenciador de pacotes do Python)

Instalação e Execução
Clone o repositório:

Bash

``https://github.com/WRodrigues12olive/Organizador_de_Pastas.git
cd seu-repositorio ``
Crie um ambiente virtual (recomendado):

```bash
# Clone o repositório
git clone https://github.com/WRodrigues12olive/Organizador_de_Pastas

# Navegue até a pasta
cd seu-repositorio

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python Organizador_de_arquivos.py

Bash

python Organizador_de_arquivos.py
```
