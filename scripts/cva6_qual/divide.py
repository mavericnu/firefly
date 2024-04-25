f_und = "undetected.txt"
with open(f_und, "r") as infile:
    content_und = infile.readlines()

f_det = "detected.txt"
with open(f_det, "r") as infile:
    content_det = infile.readlines()

UNDETECTED = {line.split("/")[6] for line in content_und if "/maveric/" in line}
DETECTED = {'a1c58b1f-d149-4834-ad15-0755025aafb9', '75c6e9bc-77a7-4ba7-9a40-cb844b4d4399', 'e381d7bf-ee69-4f34-a4da-20fcfab80ee0', '27e4fbd5-f21d-4242-b53c-e9596b1e9a70', '57dbb4c3-d680-4e9e-9beb-f5f06b2b29ea', 'd5f52405-19cf-4b1b-827d-4ce9108f0676', '7334541f-783e-4cfb-bcbd-26875428a3a6', '2c5fea76-f8b3-448e-8492-6fcf044bbd76', '3fbdf14d-618c-4acb-9228-bc89a30af6e7', '63bea7e4-a7e6-446a-8e8d-5fd141ae48ab', '84c0af7e-c255-4882-8bb7-f92b5a3e42c8', '622576d2-93e2-4b03-89e8-26e1c1a5c91e', 'de82357d-544b-46e6-88e4-b4e68d3dbf5e', '3f50c0c5-58d1-419b-81bf-7c3571d8b5c1', 'a78b9666-da68-4084-8292-293456633b55', '4dd97876-8375-4833-81e5-1a4ba09b9e4f', '300c465d-545b-4b32-a01b-5c7d6ad3bcdd', 'eee5f1ec-a33b-47a7-8ec8-1b8876011160', 'b624910c-38a0-4b70-8430-dcf10758b593', '7edf2f0b-899b-4296-a6f3-661eb58437a5', 'e3e8bb59-b0c7-454a-b2fc-8724174234ae',
            'ea6cbab5-0c19-46ec-b45c-82a038bc27bc', '25efe6f9-6e5f-4efc-87d7-2ada6a672dec', '3d412060-d14f-4f68-856c-96a367f7ab30', '95bf33fc-a3d5-4159-b295-8c7344d712e8', '6e91b2a9-84b6-4d64-9dee-9cd509cc6560', 'd8c6334f-6c8e-4f17-890d-00788596af4b', '1c7a763a-f07f-4731-9fdf-567b28f2c417', 'b9e507c1-f64e-41bf-8446-29eaed635eec', '4f81cae5-a5a1-4ace-9ad0-6d57d9186067', '46ae4583-e832-41d5-8625-c2da4ea1585b', 'eb2d12d8-ca66-470d-887f-a9f479bfe9b0', '6a140bb5-ea8b-47a3-af2f-166153cfea6d', 'a0db95cb-fe04-46a9-b8df-cdfe303346ff', '96137235-69fc-467e-ba2a-ec585a9c4be0', 'b15fc3b3-8ba3-4583-bef2-0829cccc6273', 'c242fee0-3c68-4dc2-9a02-cf4feaae641e', 'b84db9c7-6d82-4c94-a0f9-3ec009db106e', '5f57b093-3738-4e18-816b-ee808eb17209', 'cf3f8e04-6d11-4dfd-b6b3-8a0d20063179', '5198c681-e2fa-4d94-9cab-899acdcf75bb', '9b72c7b2-f87c-46af-b900-59a4fb968872'}

FRONTEND_DETECTED = {line.split("/")[6] for line in content_det if "/frontend/" in line}
FRONTEND_UNDETECTED = {line.split("/")[6] for line in content_und if "/frontend/" in line}

CACHE_SUB_DETECTED = {line.split("/")[6] for line in content_det if "/cache_subsystem/" in line}
CACHE_SUB_UNDETECTED = {line.split("/")[6] for line in content_und if "/cache_subsystem/" in line}

BACKEND_DETECTED = {line.split("/")[6] for line in content_det if ("/maveric/" in line and ("/cache_subsystem/" not in line and "/frontend/" not in line))}
BACKEND_UNDETECTED = {line.split("/")[6] for line in content_und if ("/maveric/" in line and ("/cache_subsystem/" not in line and "/frontend/" not in line))}

print(f"FRONTEND => {len(FRONTEND_DETECTED & DETECTED)} detected and {len(FRONTEND_UNDETECTED & UNDETECTED)} undetected")
print(f"CACHE SUBSYSTEM => {len(CACHE_SUB_DETECTED & DETECTED)} detected and {len(CACHE_SUB_UNDETECTED & UNDETECTED)} undetected")
print(f"BACKEND => {len(BACKEND_DETECTED & DETECTED)} detected and {len(BACKEND_UNDETECTED & UNDETECTED)} undetected")