from functools import lru_cache

from hydradxapi import HydraDX

HYDRA_MAINNET = "wss://hydradx-rpc.dwellir.com"
LOCAL = "ws://127.0.0.1:8000"

RPC = LOCAL

if __name__ == '__main__':
    hydra = HydraDX(RPC)
    hydra.connect()

    #call_function = hydra._client.api.get_metadata_call_function("Utility", "dispatch_as")
    #param_info = call_function.get_param_info()
    #print(param_info)

    votes = hydra.api.staking.position_votes()

    rv_batch = []

    print("Total staking votes: " + str(len(votes)))

    for vote in votes[:50]:
        position_id = vote.position_id
        nft = hydra.api.uniques.asset(2222, position_id)
        for v in vote.votes:
            ref_index = v.referendum_id

            @lru_cache
            def is_referendum_finished(index) -> bool:
                referendum = hydra.api.democracy.referendum_info(index)
                return "Finished" in referendum.keys()

            if is_referendum_finished(ref_index):
                # print(f"{nft['owner']} : {v.referendum_id}")
                call = hydra._client.api.compose_call(
                    call_module="Democracy",
                    call_function="force_remove_vote",
                    call_params={"target": nft["owner"], "index": v.referendum_id},
                )
                rv_batch.append(call)

    call = hydra._client.api.compose_call(
        call_module="Utility", call_function="batch", call_params={"calls": rv_batch}
    )

    print(f"batch: {call.encode()}")

    hydra.close()


