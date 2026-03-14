import random

def guess_number_game():
    print("欢迎来到猜数字游戏！")
    print("我已经想好了一个 1 到 100 之间的整数，请你来猜一猜！")
    
    target = random.randint(1, 100)
    attempts = 0
    
    while True:
        try:
            guess = int(input("请输入你的猜测（1-100）："))
            attempts += 1
            
            if guess < 1 or guess > 100:
                print("请输入 1 到 100 之间的数字！")
                continue
            
            if guess < target:
                print("小了！")
            elif guess > target:
                print("大了！")
            else:
                print(f"恭喜你，猜对了！数字是 {target}")
                print(f"你总共猜了 {attempts} 次")
                break
                
        except ValueError:
            print("请输入一个有效的整数！")

if __name__ == "__main__":
    guess_number_game()
