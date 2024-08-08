VERSION=$1
MASS=$2
ORDER=$3

mkdir plots_${VERSION}/
mkdir plots_${VERSION}/vlllimits_vs_mvll
mkdir plots_${VERSION}/vlllimits_vs_ctau

if [ "$2" == "2" ]; then
     #versus ctau(a)
     ctaus=(2 3 4 5 6 7 8 9 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90 95 100 150 200 250 300 800 1000 2000 3000 8000 10000) #mm
     for ctau in ${ctaus[@]}
     do
     	   python plot_VLLlimits_1D_mvll.py --unblind --version ${VERSION} --order ${ORDER} --mllp ${MASS} --ctau ${ctau} 
     	   python plot_VLLlimits_1D_mvll.py --unblind --version ${VERSION} --order ${ORDER} --mllp ${MASS} --ctau ${ctau} --categ
     done
     #versus m(a)
     masses=(200 300 400 500 600 700 800) #gev
     for ms in ${masses[@]}
     do
         python plot_VLLlimits_1D_ctau.py --unblind --version ${VERSION} --order ${ORDER} --mllp ${MASS} --mvll ${ms}
         python plot_VLLlimits_1D_ctau.py --unblind --version ${VERSION} --order ${ORDER} --mllp ${MASS} --mvll ${ms}   --categ
     done
elif [ "$2" == "10" ]; then
     #versus ctau(a)
     ctaus=(10 20 30 80 100 200 300 800 1000 2000 3000 8000 10000) #mm
     for ctau in ${ctaus[@]}
     do
     	   python plot_VLLlimits_1D_mvll.py --unblind --version ${VERSION} --order ${ORDER} --mllp ${MASS} --ctau ${ctau} 
     	   python plot_VLLlimits_1D_mvll.py --unblind --version ${VERSION} --order ${ORDER} --mllp ${MASS} --ctau ${ctau} --categ
     done
     #versus m(a)
     masses=(300 700 1000) #gev
     for ms in ${masses[@]}
     do
         python plot_VLLlimits_1D_ctau.py --unblind --version ${VERSION} --order ${ORDER} --mllp ${MASS} --mvll ${ms}
         python plot_VLLlimits_1D_ctau.py --unblind --version ${VERSION} --order ${ORDER} --mllp ${MASS} --mvll ${ms}   --categ
     done
else
   echo "[ERROR] Mass is not correct!"
fi