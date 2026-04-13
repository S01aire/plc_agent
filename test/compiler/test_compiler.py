from plc_agent.src.validation.compiler import matiec_compiler

file_path = "./test/compiler/test.st"

if __name__ == "__main__":
    success, errors = matiec_compiler(file_path)
    if success:
        print("编译成功!")
    else:
        print("编译失败!")
        print(errors)