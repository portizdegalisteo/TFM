export IMAGE_FAMILY="tf-latest-cpu"
export ZONE="europe-west1-b"
export INSTANCE_NAME="tfm"
export INSTANCE_TYPE="n1-standard-1"

gcloud compute instances create $INSTANCE_NAME \
        --zone=$ZONE \
        --image-family=$IMAGE_FAMILY \
        --image-project=deeplearning-platform-release \
        --maintenance-policy=TERMINATE \
        --machine-type=$INSTANCE_TYPE \
        --boot-disk-size=200GB \
        --metadata-from-file startup-script=test.sh \
        --metadata="install-nvidia-driver=True"

gcloud compute firewall-rules create tfm --allow tcp:80
gcloud compute firewall-rules create tfm --allow tcp:443
