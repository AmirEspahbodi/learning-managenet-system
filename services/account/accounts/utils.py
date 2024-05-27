import orjson
from python_ipware import IpWare
from user_agents import parse


def get_user_agent(request):
    if not hasattr(request, "META"):
        return ""
    ua_string = request.META["HTTP_USER_AGENT"]
    if not isinstance(ua_string, str):
        ua_string = ua_string.decode("utf-8", "ignore")
    user_agent = parse(ua_string)

    user_agent_json = orjson.dumps(
        {
            "browser_family ": user_agent.browser.family,
            "browser_version ": user_agent.browser.version,
            "browser_version_string ": user_agent.browser.version_string,
            "os_family ": user_agent.os.family,
            "os_version ": user_agent.os.version,
            "os_version_string ": user_agent.os.version_string,
            "device_family ": user_agent.device.family,
            "device_brand ": user_agent.device.brand,
            "device_model ": user_agent.device.model,
            "is_email_client": user_agent.is_email_client,
            "is_touch_capable": user_agent.is_touch_capable,
            "is_pc": user_agent.is_pc,
            "is_bot": user_agent.is_bot,
            "is_mobile": user_agent.is_mobile,
            "is_tablet": user_agent.is_tablet,
        }
    )
    return user_agent_json


def get_user_ip(request):
    if not hasattr(request, "META"):
        return ""
    ipw = IpWare()
    request_meta = request.META
    ip, trusted_route = ipw.get_client_ip(request_meta)
    # The 'ip' is an object of type IPv4Address() or IPv6Address() with properties like:
    if ip:
        return orjson.dumps(
            {
                "ip": str(ip),
                **(
                    {"ipv4_mapped": ip.ipv4_mapped}
                    if hasattr(ip, "ipv4_mapped")
                    else {}
                ),
                **({"is_global": ip.is_global} if hasattr(ip, "is_global") else {}),
                **(
                    {"is_reserved": ip.is_reserved}
                    if hasattr(ip, "is_reserved")
                    else {}
                ),
                **({"is_private": ip.is_private} if hasattr(ip, "is_private") else {}),
                **(
                    {"is_loopback": ip.is_loopback}
                    if hasattr(ip, "is_loopback")
                    else {}
                ),
                **(
                    {"is_multicast": ip.is_multicast}
                    if hasattr(ip, "is_multicast")
                    else {}
                ),
                **(
                    {"is_link_local": ip.is_link_local}
                    if hasattr(ip, "is_link_local")
                    else {}
                ),
                **(
                    {"is_site_local": ip.is_site_local}
                    if hasattr(ip, "is_site_local")
                    else {}
                ),
                **(
                    {"is_unspecified": ip.is_unspecified}
                    if hasattr(ip, "is_unspecified")
                    else {}
                ),
            }
        )
    return ""
