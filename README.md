# Desafio_engenharia_dados

## Descrição

Esta foi a minha resolução do desafio de engenharia de dados do processo de seleção da Lighthouse, neste projeto foi necessário extrair duas fontes de dados, uma csv e outra sql salvar estes dados localmente e depois com os dados salvos carregar-los em um banco de dados PostgresSQL. Este projeto foi realizado utilizando o sistema operacional linux.


## Configurações 

Para realizar o projeto é necessário utilizar algumas ferramentas obrigatórias do desafio, estas são: 

- Airflow
- Meltano 
- Docker 
- PostgresSQL

Então para configuração destas ferramentas e realização do projeto é necessário seguir o passo a passo a seguir.

### Preparando ambiente 

Crie uma pasta que será o repositório do seu projeto.

Clone o repositório do [desafio](https://github.com/techindicium/code-challenge) da lighthouse dentro da pasta do repositório do seu projeto.

Delete o arquivo .yml clonado.

### Instalar Docker e baixar .yml do Airflow 

Instale o [Docker engine](https://docs.docker.com/engine/install/ubuntu/) 

Vamos rodar o Airflow com o docker portanto precisamos do arquivo [docker-compose.yml](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html) do Airflow, utilize o seguinte comando:

```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.9.2/docker-compose.yaml'
```

NOTA: Utilize este comando dentro da sua pasta que será o repositório do seu projeto.

### Configurando arquivos para rodar os bancos e o Airflow com o Docker

Configurar o arquivo northwind.sql do repositório clonado do desafio: 

- Exclua todas as linhas do começo do arquivo até o comentário "drop tables";

- No inicio do arquivo escreva:

```sql
CREATE DATABASE northwind;
\c northwind
```
e salve o arquivo;

Crie um novo arquivo .sql na mesma pasta com o nome que você quer dar para o seu banco de dados final, no meu caso foi northwind_final.sql, escreva o seguinte neste arquivo:

```sql
CREATE DATABASE northwind_final;
```
e salve o arquivo;

No arquivo .yml baixado, adicione os 2 arquivos configurados anteriormente como volumes do container postgres da seguinte maneira:

```yaml
- ./data/northwind.sql:/docker-entrypoint-initdb.d/northwind.sql
- ./data/northwind_final.sql:/docker-entrypoint-initdb.d/northwind_final.sql
```

NOTA: Se o arquivos estiverem em outros locais você deverá colocar o caminho correto para os arquivos.

Ainda no arquivo .yml, adicione o arquivo docker.sock e também o seu diretório nos volumes do x-airflow-common da seguinte maneira:

```yaml
- /var/run/docker.sock:/var/run/docker.sock
- ./data/output:/opt/data/output
```

NOTA: crie uma pasta que irá receber os dados extraidos no exemplo e a pasta output. 

Por fim defina um nome para o seu container postgres, no meu caso foi postgres, da seguinte maneira:

```yaml
container_name: postgres 
```

ATENÇÃO esta etapa pode ser opcional, rode o comando:

```bash
ls -l /var/run/docker.sock
```

Caso o output desse comando retorne o arquivo como tendo o Owner e o Grupo com o valor root PULE essa etapa, caso o contrário siga as instruções a seguir:

- Execute o comando 

```bash
getent group docker
```

o output resultará em alguns nomes e um número, copie este número.

- No arquivo .yml adicone este número abaixo do "image" do x-airflow-common da seguinte maneira:

```yaml
group_add:
- número
```

Após estas configurações o airflow deve rodar junto com os bancos criados.

### Instalando meltano

Agora com o ambiente configurado vamos instalar o meltano.

Primeiramente cria-se um ambiente virtual para utilizar o meltano:

```bash
python3 -m venv .venv
```

Entre no seu ambiente virtual:

```bash
source .venv/bin/activate
```

Instale o meltano:

```bash
pip install meltano
``` 

Inicie um projeto no meltano:

```bash
meltano init nomedapastadoseudesafio
```


NOTA: Rode estes comandos dentro da pasta que será o repositório do seu projeto.

Após o projeto criado, entre na pasta do seu projeto meltano.

### Configurando o meltano

Agora com o meltano instalado e o seu projeto criado, vamos instalar alguns plugins para que possa ser necessário realizar o desafio.

Primeiramente os extractors que serão utilizados para extrair os dados dos arquivos CSV e SQL.

```bash
meltano add extractor tap-csv
```
```bash
meltano add extractor tap-postgres
```

Agora os loaders que serão utilizados para carregar os dados extraidos.

```bash
meltano add loader target-csv
```
```bash
meltano add loader target-postgres
```

E por fim um mapper que conseguirá mapear o valor de uma coluna para o tipo string.

```bash
meltano add mapper meltano-map-transformer
```

Após instalar estes plugins, é necessário acessar o arquivo meltano.yml para configurar estes plugins de acordo com a necessidade do desafio.

NOTA: Os plugins que necessitam dos dados do postgres para acerssá-lo deve-se passar os dados que temos no arquivo docker-compose.yml configurado nas etapas anteriores.

NOTA2: Nos arquivos loaders target-csv devem ser configurados como destination_path o diretório colocado no arquivo docker_compose.yaml, no nosso exemplo, /opt/data/output.

Após as configurações realizadas pode-se criar jobs no meltano que realizarão as etapas que o desafio exige, para criar um job no meltano digite o seguinte comando:

```bash
meltano job add nomedoseujob --tasks "nomedoextrator nomedoloader"
```

Desta maneira ao executar estes jobs ele irá extrair e carregar os dados de acordo com o job rodado. 

### Build de uma imagem do nosso projeto no meltano 

Para que possamos usar o nosso projeto do meltano em nossa Dag do Airflow será necessário contruir uma imagem docker dele, para isso siga os seguintes passos:

Dentro da pasta do projeto utilize o comando:

```bash
meltano add files files-docker
```

Será adicionado um arquivo chamado Dockerfile que contém as instruções de como montar a imagem do nosso projeto meltano, para isso basta utilizar um comando dando o nome do projeto e a versão como no exemplo abaixo:

```bash
docker build -t nomedoprojetomeltano:versãodoprojeto .
```

Desta maneira nossa imagem docker do projeto será montada e estará pronta para ser utilizada.

### Iniciando o Airflow e carregando os bancos criados 

Antes de ser dado o comando para subir o Airflow é necessário definir uma variável de ambiente, basta executar o seguinte comando:

```bash
export AIRFLOW_UID=$(id -u)
```

Agora dentro da pasta que está o seu arquivo docker-compose.yml utiliza o comando:

```bash
docker compose up
```

Depois de um tempo o Airflow já deve estar no ar e pode ser acessado pelo navegador pela url: localhost:8080 (usuário: airflow, senha: airflow). 

### Configurando a Dag

Para criar sua dag, basta criar um arquivo .py dentro da pasta dags do repositório do seu projeto.

Como vamos utilizar a imagem docker do nosso projeto do meltano será necessário utilizar o DockerOperator na dag, é necessário algumas configurações para isso não ter falhas de conexão, para isso na função em que irá utilizar o DockerOperator se deve passar como parâmetro as seguintes informações:

No parâmetro "image" você irá passar o nome:versão da imagem docker construida nos passos anteriores da seguinte maneira:

```py
image='nomedoprojetomeltano:versãodoprojeto'
```

No parâmetro "network_mode" vamos colocar o container:nomedocontainer, lembrando que colocamos o nome do container nas etapas anteriores, o exemplo fica assim:

```py
network_mode='container:postgres'
```

Para ao rodar a Dag os arquivos serem salvos localmente, é necessário declarar o parâmetro "mounts", sendo o source o caminho onde você quer que os arquivos sejam salvos localmente e o target para o local do container em que você quer que os arquivos sejam salvos, siga o exemplo a seguir:

```py
mounts = [
        Mount(
            source='/local/sua/maquina/data',  
            target='/opt/data',  
            type='bind',
        ),
]
```

Por fim deve-se declarar a "docker_url" da mesma maneira que foi passado no arquivo .yml, siga o exemplo:

```py
        docker_url="unix://var/run/docker.sock",
```

Pronto desta forma a conexão deve ser bem sucedida.

### Criando a Dag

Agora para realizar o desafio devemos fazer tasks dentro da Dag que realizem os pipelines criados do nosso projeto meltano desta forma extraindo os dados do arquivo CSV e SQL e carregando-os no disco local e depois do disco local para um banco de dados PostgresSQL. Para realizar este processo foi criado uma task para extrair arquivos CSVs e carregar em arquivos CSVs, uma task para extrair arquivos de um banco de dados PostgresSQL e carregar em arquivos CSVs, uma task que extrai arquivos CSVs e carrega em um banco de dados PostgresSQL, vale lembrar que nestas tasks iremos rodar os jobs que criamos no meltano cada job com sua respectiva task. 

Com estas tasks criadas é necessário fazer uma função que irá criar as pastas dinamicamente em nosso diretório local de acordo como foi especificado no desafio [/data/postgres/{table}/2024-01-01/file.format]. Para fazer esta função funcionar também devemos fazer uma task dela que chamará esta função, onde a task só irá criar as pastas após ter acontecido a extração dos dados.

```py
[extrai_csv_para_csv, extrai_postgres_para_csv] >> cria_pastas >> extrai_csv_para_postgres 
```

### Conclusão 

Este processo seletivo foi realmente um desafio para mim, estou em um período que estou tentando voltar a trabalhar na área, apesar de não ter muita experiência decidi realizar o desafio para testar os meus conhecimentos e concorrer a uma vaga que eu considero uma ótima oportunidade para quem esta querendo ingressar na área e contruir uma carreira, para realizar o desafio foi necessário muito tempo lendo documentações e pesquisando erros nos mais diferentes sites com informações condizentes ao desafio, tive muita dificuldade com as configurações do docker-compose.yml para fazer ele rodar o airflow junto com o banco de dados inicial e final e também fazer as conexões com meu diretório e o container da imagem do docker, após muitos testes e "dor de cabeça" foi possivel realizar esta etapa, porém no momento de rodar a Dag, por algum motivo o loader do postgres não estava funcionando, a task não da nenhum log de erro, porém ao entrar no banco de dados final ele esta vazio. Apesar do resultado fiquei satisfeito com o meu desempenho no desafio, aprendi muito neste curto período e me afeiçoei ainda mais a área da engenharia de dados.













