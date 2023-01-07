# Speech-to-text model tester

### Docker

```shell
docker build -t model-tester .
```
```shell
docker run --gpus all -d --name whisper-tester -it model-tester -e GoogleAPI=<YOUR KEY>
```