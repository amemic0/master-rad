from kubernetes import client, config
import yaml

yaml_file = "/home/dwh/Desktop/MasterRad/network/network_policy.yaml"
namespace = "master-rad"
def load_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def apply_network_policy(yaml_file, namespace):
    config.load_kube_config()

    api_instance = client.NetworkingV1Api()
    policy_body = load_yaml(yaml_file)

    try:
        existing_policies = api_instance.list_namespaced_network_policy(namespace)
        policy_names = [p.metadata.name for p in existing_policies.items]

        if policy_body["metadata"]["name"] in policy_names:
            response = api_instance.replace_namespaced_network_policy(
                name=policy_body["metadata"]["name"],
                namespace=namespace,
                body=policy_body
            )
            print(f"NetworkPolicy '{policy_body['metadata']['name']}' je ažuriran.")
        else:
            response = api_instance.create_namespaced_network_policy(
                namespace=namespace, 
                body=policy_body
            )
            print(f"NetworkPolicy '{policy_body['metadata']['name']}' je kreiran.")

    except client.exceptions.ApiException as e:
        print(f"Greška prilikom primjene NetworkPolicy-ja: {e}")

apply_network_policy(yaml_file, namespace)
