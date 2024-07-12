#FEE_FACTOR = (100 - 0.3) / 100
FEE_FACTOR = 1


def univ2_trade(token0_units_reserve: float, token1_units_reserve: float, token0_amount_sold):
    # usdc: token 0
    # zerc: token 1

    liquidity = token0_units_reserve * token1_units_reserve
    token0_units_after = token0_units_reserve + token0_amount_sold
    token1_units_after = liquidity / token0_units_after
    token1_bought_amount = token1_units_reserve - token1_units_after
    amount_after_fee = token1_bought_amount * FEE_FACTOR
    return amount_after_fee


if __name__ == '__main__':

    for guess in range(200):
        eth_reserve_usdc_units = 207539  # (x before)
        eth_reserve_zerc_units = 1445860  # (y before)
        eth_usdc_amount_sold = guess
        zerc_eth = univ2_trade(eth_reserve_usdc_units,eth_reserve_zerc_units,eth_usdc_amount_sold)

        polygon_reserve_usdc_units = 59833
        polygon_reserve_zerc_units = 415549
        usdc_polygon = univ2_trade(polygon_reserve_zerc_units,polygon_reserve_usdc_units, zerc_eth)

        profit = usdc_polygon - eth_usdc_amount_sold
        print(guess, profit)

