array=(55 79 111 108 152 49 164 53 94 105 65 40 90 32 89 162 122 137 51 21 6 71 83 81 126 4 22 100 171 20 116 1 25 35 174 46 156 70 78 124 27 97 85 133 37 98 19 125 31 56 121 74 160 114 168 18 88 0 36 173 69 118 167 14 38 139 161 5 9 10 134 91 16 128 176 7 15 165 117 72 52 61 66 63 95 12 136 131 58 149 177 64 45 60 141 132 107 151 17 169 47 82 3 104 33 123 166 28 77 159 67 135 42 96 129 113 154 68 23 57 30 140 150 106 143 48 178 101 75 153 120 86 87 142 2 148 26 138 43 8 175 163 44 144 102 119 127 54 112 73 99 41 84 109 115 158 76 24 145 146);
for i in "${array[@]}"; do echo $i; python smatch.py -f ../tiburon-tar-gz_2/amr_train_smr_tree/smr$i.txt ../tiburon-tar-gz_2/amr_train_single/generate$i.txt; done;