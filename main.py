from web3 import Web3


def calc_arbitrage(usdc_amount_eth_pool: int, zerc_amount_eth_pool: int, usdc_amount_polygon_pool: int, zerc_amount_polygon_pool: int) -> tuple[float, int, int, int, int]:

    # connect to infura
    eth_w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/fc7a17cf5af743bb8c67eb6c71aa085f'))
    polygon_w3 = Web3(Web3.HTTPProvider('https://polygon-mainnet.infura.io/v3/fc7a17cf5af743bb8c67eb6c71aa085f'))

    # connect to ethereum contract
    eth_contract_abi = open("eth_contract_abi.json", "r").read()
    eth_contract_address = eth_w3.to_checksum_address("0x29eBA991F9D9E71C6bBd69cb71c074193fd877Fd")
    eth_contract = eth_w3.eth.contract(address=eth_contract_address, abi=eth_contract_abi)

    # find reserves of both coins in ethereum
    eth_reserves = eth_contract.functions.getReserves().call()
    eth_usdc_reserve = eth_reserves[0]
    eth_zerc_reserve = eth_reserves[1]

    # connect to polygon contract
    polygon_contract_abi = open("polygon_contract_abi.json", "r").read()
    polygon_contract_address = polygon_w3.to_checksum_address("0x514480cF3eD104B5c34A17A15859a190E38E97AF")
    polygon_contract = polygon_w3.eth.contract(address=polygon_contract_address, abi=polygon_contract_abi)

    # find reserves of both coins in polygon
    polygon_reserves = polygon_contract.functions.getReserves().call()
    polygon_usdc_reserve = polygon_reserves[0]
    polygon_zerc_reserve = polygon_reserves[1]

    # considering decimals to get the pricing accurate
    usdc_decimals = 6
    zerc_decimals = 18

    # calculating zerc per usdc ratio in each network from reserves
    zerc_per_usdc_eth = (eth_zerc_reserve / eth_usdc_reserve) / (10 ** (zerc_decimals - usdc_decimals))
    zerc_per_usdc_polygon = (polygon_zerc_reserve / polygon_usdc_reserve) / (10 ** (zerc_decimals - usdc_decimals))

    # the main idea is to buy zerc where we get more units per usdc, and sell it where we get more usdc units

    # what network is to buy zerc with usdc and what network is to sell zerc back to usdc
    zerc_buy_net, zerc_sell_net = ("eth", "polygon") if zerc_per_usdc_eth > zerc_per_usdc_polygon else ("polygon", "eth")

    # calculate the maximum possible zerc we can buy, consider the limits of usdc and zerc amounts in noth netowrks
    if zerc_buy_net == "eth":
        max_possible_zerc_buy = min(zerc_amount_eth_pool, usdc_amount_eth_pool * zerc_per_usdc_eth)
        max_possible_zerc_sell = usdc_amount_polygon_pool / zerc_per_usdc_polygon
        zerc_to_buy = min(max_possible_zerc_buy, max_possible_zerc_sell)

        # return values
        traded_eth_zerc = zerc_to_buy
        traded_eth_usdc = zerc_to_buy / zerc_per_usdc_eth
        traded_polygon_zerc = zerc_to_buy
        traded_polygon_usdc = zerc_to_buy / zerc_per_usdc_polygon

    else:
        max_possible_zerc_buy = min(zerc_amount_polygon_pool, usdc_amount_polygon_pool * zerc_per_usdc_eth)
        max_possible_zerc_sell = usdc_amount_polygon_pool / zerc_per_usdc_polygon
        zerc_to_buy = min(max_possible_zerc_buy, max_possible_zerc_sell)

        # return values
        traded_polygon_zerc = zerc_to_buy
        traded_polygon_usdc = zerc_to_buy / zerc_per_usdc_polygon
        traded_eth_zerc = zerc_to_buy
        traded_eth_usdc = zerc_to_buy / zerc_per_usdc_eth

    # inversing the ratio to get expected profit
    usdc_per_zerc_eth = 1 / zerc_per_usdc_eth
    usdc_per_zerc_polygon = 1 / zerc_per_usdc_polygon
    profit_per_zerc_traded = abs(usdc_per_zerc_eth - usdc_per_zerc_polygon)

    expected_profit = zerc_to_buy * profit_per_zerc_traded
    return expected_profit, traded_eth_zerc, traded_eth_usdc, traded_polygon_zerc, traded_polygon_usdc


if __name__ == '__main__':
    calc_arbitrage(1000, 6000, 1000, 6000)