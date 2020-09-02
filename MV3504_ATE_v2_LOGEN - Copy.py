    def logen_cal(self, tssi_out_lim = 965, band_overide = None, prnt=False):
        size_dict = {"LB":{"LOGEN_multGateBias_28G":[0,8,1],
                           "LOGEN_multbuffbias_28G":[0,8,1],
                           "LOGEN_PA1Ibias_28G":[8,32,1],
                           "LOGEN_multCtune_28G":[0,121,8],
                           "LOGEN_multbuffCtune_28G":[0,121,8],
                           "LOGEN_PACtune_28G":[0,16,1],
                           "init_bias_1" : [3,3,20],
                           "init_bias_2" : [3,0,16]
                           },
                     "HB":{"LOGEN_multGateBias_39G":[0,8,1],
                           "LOGEN_multbuffbias_39G":[0,8,1],
                           "LOGEN_PA1Ibias_39G":[0,32,1],
                           "LOGEN_multCtune_39G":[0,4,1],
                           "LOGEN_multbuffCtune_39G":[0,2,1],
                           "LOGEN_PACtune_39G":[0,2,1],
                           "init_bias_1" : [10,10,20],
                           "init_bias_2" : [10,0,16]
                           }
                     }
        if band_overide is not None:
            band = band_overide.upper()
        else:
            band_set = getattr(self.reg,"LOGEN_HighBand_sel").val 
            band = "HB" if (band_set==1) else "LB"
        if band not in size_dict.keys():
            print("Invalid Band Selection, choose from LB/HB")
            return 0 
        band_freq = "28G" if (band == "LB") else "39G"
        band_comp = "HB" if (band =="LB") else "LB"
        cap_reg_list = ["LOGEN_multCtune_%s"%band_freq,"LOGEN_multbuffCtune_%s"%band_freq,"LOGEN_PACtune_%s"%band_freq]
        tssi_blk_set = ['%s_TSSI_MULT'%band,'%s_TSSI_BUFF'%band,'%s_TSSI_PA1'%band]  # LOGEN_pu_tssi_multbuff_28G ???
        self.logen_pu(band = band_comp, pu = 0 , tssi_pu = 0)
        self.logen_pu(band = band, pu = 1 , tssi_pu = 1)
        tssi_out_low = tssi_out_lim*0.99
        tssi_out_high = tssi_out_lim*1.01
        self.set_ana_mux(option="logen")
        self.set_logen(band = band, mult_bias = size_dict[band]["init_bias_1"][0], buff_bias = size_dict[band]["init_bias_1"][1], pa_bias = size_dict[band]["init_bias_1"][2], mult_ctune = 50, buff_ctune = 50, pa_ctune=10)
        for i in range(len(cap_reg_list)):
            self.enable_tssi(block=tssi_blk_set[i])
            res = []
            cap_start = size_dict[band][cap_reg_list[i]][0]
            cap_stop = size_dict[band][cap_reg_list[i]][1]
            cap_step = size_dict[band][cap_reg_list[i]][2]
            cap_list = list(numpy.arange(cap_start,cap_stop,cap_step))
            for cap_val in range(len(cap_list)):
                getattr(self.reg,"%s"%cap_reg_list[i]).val = cap_list[cap_val]
                res.append(self.read_tssi()[0])
            max_cap_val = cap_list[res.index(max(res))]
            getattr(self.reg,"%s"%cap_reg_list[i]).val = max_cap_val
        self.enable_tssi(block='%s_TSSI_PA1'%band)
        save_sett = self.save_logen(band = band,prnt=False)
        self.set_logen(band =band, mult_bias = size_dict[band]["init_bias_2"][0], buff_bias = size_dict[band]["init_bias_2"][1], pa_bias = size_dict[band]["init_bias_2"][2], mult_ctune = save_sett[4], buff_ctune = save_sett[5], pa_ctune=save_sett[6])

        for bias_reg in ["LOGEN_multGateBias_%s"%band_freq,"LOGEN_PA1Ibias_%s"%band_freq,"LOGEN_multbuffbias_%s"%band_freq]:
            bias_start = size_dict[band][bias_reg][0]
            bias_stop = size_dict[band][bias_reg][1]
            bias_step = size_dict[band][bias_reg][2]
            bias_list = list(numpy.arange(bias_start,bias_stop,bias_step))
            for bias_tune in bias_list:
                getattr(self.reg, bias_reg).val = bias_tune
                readout =(self.read_tssi(vref=0, return_format='ADC', clk_div=32, prnt=False)[0])
                print(bias_reg,bias_tune,readout)
                if ((readout<=tssi_out_high) and (readout>=tssi_out_low)):
                    print("LOGEN_CAL_DONE")
                    getattr(self.reg, "LOGEN_PA2Ibias_%s"%band_freq).val = getattr(self.reg, "LOGEN_PA1Ibias_%s"%band_freq).val
                    save_sett = self.save_logen(band = band,prnt=prnt)
                    return 0
                if (readout>=tssi_out_high):
                    break
        print("LOGEN_CAL_terminated")
        getattr(self.reg, "LOGEN_PA2Ibias_%s"%band_freq).val = getattr(self.reg, "LOGEN_PA1Ibias_%s"%band_freq).val
        save_sett = self.save_logen(band = band,prnt=prnt)
        self.clear_tssi()
        self.clear_ana_mux()
        return 0 