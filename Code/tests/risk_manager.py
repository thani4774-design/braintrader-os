def calculate_stop_loss(price, atr):

    stop_loss = price - (atr * 2)

    return round(stop_loss, 2)



def calculate_target(price, atr):

    target = price + (atr * 4)

    return round(target, 2)