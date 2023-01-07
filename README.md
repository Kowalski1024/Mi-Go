# Speech-to-text model tester

### Docker

```shell
docker build -t model-tester .
```
```shell
docker run  -e GoogleAPI=<YOUR KEY> --gpus all -d --name whisper-tester -it model-tester
```