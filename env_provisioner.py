import os
import shutil
import tarfile

MOCKUP_SRC_TARBALL=os.path.join('mockups', 'env_provisioner', 'src_tarball', 'conv-codelets-master.tar.gz')
MOCKUP_DATA_TARBALL=os.path.join('mockups', 'env_provisioner', 'data_tarball', 'data.tar.gz')

def setup_environ(service_dir, src_url, data_url, docker_file):
    download_dir=os.path.join(service_dir, 'download')
    os.makedirs(download_dir)
    print("Setting up environment...")
    src_dir=os.path.join(service_dir, 'code', 'src')
    #os.makedirs(src_dir)
    print('Downloading source code', src_url, src_dir)
    src_tarball_name=os.path.basename(src_url)
    src_tarball_file=os.path.join(download_dir, src_tarball_name)
    #response = requests.get(src_url)
    #open(src_tarball_file, 'wb').write(response.content)
    print('MOCKUP downloading src tarball')
    shutil.copyfile(MOCKUP_SRC_TARBALL, src_tarball_file)

    #data_dir=os.path.join(service_dir, 'data')
    #os.makedirs(data_dir)
    print('MOCKUP downloading data tarball')
    data_tarball_name=os.path.basename(data_url)
    data_tarball_file=os.path.join(download_dir, data_tarball_name)
    shutil.copyfile(MOCKUP_DATA_TARBALL, data_tarball_file)


    full_src_dir=extract_tarball(service_dir, download_dir, src_tarball_name, src_tarball_file, 'code')
    full_data_dir=extract_tarball(service_dir, download_dir, data_tarball_name, data_tarball_file, 'data')
    ov_run_dir = os.path.join(service_dir, 'ov_runs')
    os.makedirs(ov_run_dir)
    generated_image = 'MOCKUP_IMG'
    print(f'MOCKUP: build image using {docker_file} to generate image {generated_image}')
    return full_src_dir, full_data_dir, ov_run_dir, generated_image

def extract_tarball(service_dir, download_dir, src_tarball_name, src_tarball_file, dest_dir):
    with tarfile.open(src_tarball_file) as zip_ref:
        zip_ref.extractall(download_dir)
    extracted_dir=src_tarball_name.split('.')[0]
    print(src_tarball_name)
    print(extracted_dir)
    shutil.move(os.path.join(download_dir, extracted_dir), service_dir)
    full_dest_dir = os.path.join(service_dir, dest_dir)
    os.rename(os.path.join(service_dir, extracted_dir), full_dest_dir)
    return full_dest_dir