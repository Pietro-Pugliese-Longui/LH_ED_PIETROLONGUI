# Desafio_engenharia_dados

## Descrição

Esta foi a minha resolução do desafio de engenharia de dados do processo de seleção da Lighthouse, neste projeto foi necessário extrair duas fontes de dados, uma csv e outra sql salvar estes dados localmente e depois com os dados salvos carregar-los em um banco de dados PostgresSQL. Este projeto foi realizado utilizando o sistema operacional linux Mint.


## Configurações 

Para realizar o projeto é necessário utilizar algumas ferramentas obrigatórias do desafio, estas são: 

- Airflow
- Meltano 
- Docker 
- PostgresSQL

Então para configuração destas ferramentas e realização do projeto é necessário seguir o passo a passo a seguir.

### Preparando ambiente 

Primeiramente clone o repositório do desafio.

Instale o [Docker engine](https://docs.docker.com/engine/install/ubuntu/)

Agora para fazer com que o Airflow funcione com o docker é necessário exportar algumas variáveis de ambiente primeiramente o id:

```bash
export AIRFLOW_UID=$(id -u)
```
Agora precisa exportar o grupo do docker no usuário do airflow, para isto utilize o comando:

```bash
getent group docker
```
Este comando retornará um número, decore este número, ele sera o valor que será passado na próxima váriavel de ambiente:

```bash
export DOCKER_GID= <número>
```
Com estas etapas realizadas o seu ambiente esta configurado para rodar o airflow com o docker sem problemas de conexão. Foi necessário realizar estas etapas para não haver conflito em usuários e grupos do airflow com o docker. 

### Build da imagem do projeto meltano 

Para que possamos usar o nosso projeto do meltano em nossa Dag do Airflow será necessário contruir uma imagem docker dele, para isso siga os seguintes passos:

Dentro da pasta desafio utilize o comando:

```bash
docker build -t nomedoprojetomeltano:versãodoprojeto .
```

NOTA: A Dag esta configurada como : <meltano-lighthouse:latest>, caso a imagem seja buildada com outro nome e versão, será necessário realizar essa alteração no código da Dag.

Desta maneira nossa imagem docker do projeto será montada e estará pronta para ser utilizada.

### Iniciando o Airflow 

Agora para iniciar o Airflow agora basta utilizar o comando:

```bash
docker compose up
```
Vale lembrar que é necessário as váriaveis de ambiente terem sido declaradas em um dos passos anteriores se não esta etapa terá problemas de conexão. Depois de um tempo o Airflow já deve estar no ar e pode ser acessado pelo navegador pela url: localhost:8080 (usuário: airflow, senha: airflow). 

### Configurando a Dag

Agora no arquivo da dag existem algumas configurações que deveram ser realizadas para que as tasks sejam realizadas com sucesso,
siga as intruções:

- O "mounts" declarado na dag possui o atributo "source" este atributo deverá ser configurado de acordo com o caminho absoluto da raiz do seu repositório, existe um comentário no código explicitando o local em que essa informação deve ser adicionada.

- A "image" nas tasks deve ter o nome e a versão igual a que foi buildada no passo anterior, se não as tasks não seram realizadas, existe um comentário no código explicitando o local em que deve ser feita essa configuração.

### Executando a Dag

Com todas estas etapas realizadas a Dag deve estar funcionando corretamente, agora dentro da aplicação do airflow, basta procurar pela Dag e ativar-lá deste modo as tasks seram efetuadas e você terá os arquivos csv carregados e separados em suas respectivas pastas no seu disco local, como também o banco de dados postgresSQL final montado.

### Conclusão 

Este processo seletivo foi realmente um desafio para mim, estou em um período que estou tentando voltar a trabalhar na área, apesar de não ter muita experiência decidi realizar o desafio para testar os meus conhecimentos e concorrer a uma vaga que eu considero uma ótima oportunidade para quem esta querendo ingressar na área e construir uma carreira, para realizar o desafio foi necessário muito tempo lendo documentações e pesquisando erros nos mais diferentes sites com informações condizentes ao desafio, tive muita dificuldade com as configurações do docker-compose.yml para fazer ele rodar o airflow com o docker e os bancos de dados, após muitos testes e "dor de cabeça" foi possivel realizar esta etapa. As configurações realizadas nas Dags e arquivo meltano.yml passaram por várias versões e testes até conseguirem realizar as pipelines da maneira correta. Por fim fiquei muito satisfeito com o resultado do desafio, aprendi muito em pouco tempo e utilizei todo o tempo do prazo de entrega para aprender mais e dar o meu melhor, foi muito desafiador mas ao mesmo tempo muito gratificante.













