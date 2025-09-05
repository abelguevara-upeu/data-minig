# Machine Learning projects with docker

Proyectos de machine learning con python y R (opcional)

* [Resources sharing to docker](#resources-sharing-to-docker)
* [Runing form Docker](#runing-form-Docker)
* [R en Notebook (opcional)](#r-en-notebook-opcional)
* [License](#license)

## Resources sharing to docker

	Add D:\dockr

Dockerfile
```bash
FROM continuumio/anaconda3
ADD requirements.txt /
RUN pip install -r requirements.txt
CMD ["/opt/conda/bin/jupyter", "notebook", "--notebook-dir=/opt/notebooks", "--ip='*'", "--no-browser", "--allow-root"]

```

docker-compose.yaml
```bash
version: '2'
services:
  anaconda:
    container_name: ml
    build: .
    volumes:
      - "./notebooks:/opt/notebooks"
    ports:
      - "3131:8888"

```


### Runing form Docker

Get and runing docker project

```bash
PS D:\dockr>git clone https://github.com/202ml/202ml.git
PS D:\dockr>cd 202ml 

PS D:\dockr\202ml> docker-compose up --build

```

Copiar el token y pegar en http://localhost:3131

Luego ir al modelo base http://localhost:3131/notebooks/202ml/tree/DT.ipynb


En otra terminal puede ver que el servicio  ya corre
```bash
PS D:\dockr\202ml> docker ps
CONTAINER ID        IMAGE                         COMMAND                  CREATED             STATUS              PORTS                    NAMES
845d4d868b87        202ml_anaconda                "/opt/conda/bin/jupy…"   6 weeks ago         Up 4 days           0.0.0.0:3131->8888/tcp   ml

```

Si quiere correr en back, ejecute
```bash
PS D:\dockr\202ml> docker-compose up -d

```
Ir a  http://localhost:3131/ 


(opcional) si deseas instalar algunas librerias adicionales, por ejemplo [R en Notebook](#r-en-notebook), ingrese al contenedor

```bash
PS D:\dockr\202ml> docker exec -it ml bash

(base) root@845d4d868b87:/#   
```

### R en Notebook (opcional)

Cuando esto no funciona
```bash
conda install -c r r-essentials
```
En el contenedor

En win o linux instale R: 
```bash
(base) root@845d4d868b87:/#apt update
(base) root@845d4d868b87:/#apt install r-base
(base) root@845d4d868b87:/#apt install build-essential

```
(base) root@845d4d868b87:/# sudo apt update

Ingrese al shell de R y ejecute:
```bash
(base) root@845d4d868b87:/#R 

>install.packages('IRkernel')
>IRkernel::installspec()
[InstallKernelSpec] Installed kernelspec ir in /root/.local/share/jupyter/kernels/ir
> q()
Save workspace image? [y/n/c]: y
(base) root@845d4d868b87:/#     
```
Ver https://irkernel.github.io/installation


### License



GNU, see [LICENSE](LICENSE).

Equipo de investigación y desarrollo: 
- angeli@upeu.edu.pe, 
