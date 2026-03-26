import io
path = r"f:\study\tracker\backend\app\services\betting_plan_service.py"
with io.open(path, 'r', encoding='utf-8') as f:
    for lineno, line in enumerate(f, start=1):
        if '、' in line:
            print(lineno, line.strip())
        if '\u3001' in line:
            print('U3001 literal at', lineno, line.strip())
print('done')

