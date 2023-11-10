#!/bin/bash

INPUT_DIR="docker_data/input";


function setup_folders(){
  mkdir -p docker_data/{input,output};
  input_dir=${INPUT_DIR}/$1;
  mkdir -p ${input_dir}/tmp/;
  mkdir -p ${input_dir}/{NATIVE,PREDS};
}
function clone_and_copy_data(){
  input_dir=${INPUT_DIR}/$1;
  git clone --depth 1 https://github.com/Tan-group/rsRNASP.git ${input_dir}/tmp;
}
function change_data_format_order(){
  input_dir=${INPUT_DIR}/$1;
  pdb_dir=$(find ${input_dir}/tmp/$1 -maxdepth 1 -mindepth 1 -type d | grep -v "DI" | grep -v "RMSD")
  for dir in $pdb_dir; do
    name=$(basename $dir);
    mkdir -p ${input_dir}/PREDS/${name};
    cp ${dir}/${name}.pdb ${input_dir}/NATIVE/;
    mv ${dir}/*.pdb ${input_dir}/PREDS/${name}/;
  done
  rm -rf ${input_dir}/tmp;
}
function install_data(){
  setup_folders $1;
  clone_and_copy_data $1;
  change_data_format_order $1;
  mv ${INPUT_DIR}/$1 ${INPUT_DIR}/$2;
}

install_data "PM_decoy_set" "TestSetII";
#install_data "Training_decoy_set";