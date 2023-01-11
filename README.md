# Speech-to-text model tester

### Docker

```shell
docker build -t model-tester .
```
```shell
docker run  -e GoogleAPI=<YOUR KEY> --gpus all -d --name whisper-tester -it model-tester
```

### Example
Testplan generation
```shell
python testplan_generator/testplan_generator.py ./testplans 2 -c 28 -l en
```

Run test
```shell
python tests/transcript_diff.py base "/app/testplans/<TESTFILE>" -it 2
```
