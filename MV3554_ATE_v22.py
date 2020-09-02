#$Author: Vijay $
#$LastChangedDate: 2019-10-21 03:37:57 +1000 (Mon, 21 Oct 2019) $
from . import objects
from time import sleep
from .  import chips_init_2 as c
# from objects import ChipModel
import logging, math, numpy
gr = (math.sqrt(5) - 1) / 2

# Create a generic MV3554 class for A0, B0, ... to inherit from
# Any functions which can be shared between generations can be
# defined here
class MV3554_Generic(objects.ChipModel):
	def __init__(self, chip_id, address_width, data_width, data_registers, registers):
		super(MV3554_Generic,self).__init__(chip_id, address_width, data_width, data_registers, registers)

class MV3554A0(MV3554_Generic):
	def __init__(self, chip_id, address_width, data_width, data_registers, registers):
		super(MV3554A0,self).__init__(chip_id, address_width, data_width, data_registers, registers)

	def initialize_FPGA(self, chain=9, loc=0, length=None):
		if length == None:
			if chain == 9:
				length = 1
			elif chain == 8:
				length = 4
			else:
				length = 2
		self.comms.write_reg(0x13, 0x88)
		self.comms.write_reg(0x11, (chain << 4) + (length - 1))
		self.comms.write_reg(0x12, 1 << loc)
		self.chain = chain
		self.loc = loc

	def get_chain_loc(self):
		reg_0x11 = self.comms.read_reg(0x11)
		reg_0x12 = self.comms.read_reg(0x12)
		return reg_0x11 >> 4, reg_0x12
		
	def getFirmwareVersion(self):
		print("I'm MV3554 A0. Im running firmware version %d"%(self.comms.read_reg(20)))

	#Dictionary Format - TSSI_block : [pu_reg,adc_sel,logen_testmux_sel]
	blk_dict = {"LB_TSSI_PA2" : ["LOGEN_pu_tssi_PA2_28G",1,0],
				"LB_TSSI_PA1" : ["LOGEN_pu_tssi_PA1_28G",1,1],
				"LB_TSSI_PAdr" : ["LOGEN_pu_tssi_PAdr_28G",1,2],
				"LB_TSSI_BUFF" : ["LOGEN_pu_tssi_multbuff_28G",1,3],
				"LB_TSSI_MULT" : ["LOGEN_pu_tssi_mult_28G",1,4],
				"LB_VDD0P9_PA" : ["LOGEN_pu_tssi_PAdr_28G",1,5],
				"HB_TSSI_PA2" : ["LOGEN_pu_tssi_PA2_39G",1,6],
				"HB_TSSI_PA1" : ["LOGEN_pu_tssi_PA1_39G",1,7],
				"HB_TSSI_PAdr" : ["LOGEN_pu_tssi_PAdr_39G",1,8],
				"HB_TSSI_BUFF" : ["LOGEN_pu_tssi_multbuff_39G",1,9],
				"HB_TSSI_MULT" : ["LOGEN_pu_tssi_mult_39G",1,10],
				"HB_VDD0P9_PA" : ["LOGEN_pu_tssi_PAdr_39G",1,11]
				}

##Initializes the PLL and configures 28G buffers(default init)
	def initialize_IDLE(self, chain=9, loc=0, 
	_reset=False, SPI_length=1):
		self.initialize_FPGA(chain, loc, SPI_length)
		if not bypass_reset or self.simulate_read:
			for reg in self.reg.array:
				reg.val = reg.reset
##Set BG Registers (bias, temp threshold, idac mag and slope) and Trigger BG cal RTL
		self.dreg.bg_6.val = 15
		self.dreg.bg_7.val = 128
		self.dreg.bg_8.val = 128
		self.dreg.bg_9.val = 128
		self.dreg.bg_10.val = 128
		self.dreg.bg_11.val = 128
		self.dreg.bg_12.val = 128
		self.dreg.bg_13.val = 128
		self.dreg.bg_14.val = 128
		self.dreg.bg_3.val = 0
		self.dreg.bg_2.val = 5
		self.dreg.bg_4.val = 0
		self.dreg.bg_5.val = 0
		self.run_BG_cal_rtl()
##Set Loop filter RC and comparator thresholds
		self.dreg.LF_1.val = 15
		self.dreg.LF_2.val = 0
		self.dreg.LF_3.val = 1
		self.reg.LF_Detector1con.val = 7
		self.reg.LF_Detector2con.val = 127
		self.reg.LF_bypass_DC.val = 0
##Set mmdiv and pfdcp ldo and pu regs
		self.dreg.mmd_1.val = 33
		self.dreg.pfdcp_1.val = 64
		self.dreg.pfdcp_2.val = 20
		self.dreg.pfdcp_3.val = 10
		self.dreg.pfdcp_4.val = 22
##Set SD regs - load integer and fractional values for output frequency
		self.reg.SD_frac.val = 536870912
		self.reg.SD_int.val = 42
		self.reg.SD_prbs_seed.val = 0
		self.reg.SD_reset_rng.val = 1
		self.reg.SD_reset_sd.val = 0
## Set VCO regs (bias, cap banks, ldo, pu)
		self.dreg.VCO_1.val = 90
		self.dreg.VCO_2.val = 24
		self.reg.VCO1_capbank_con.val = 300
		self.reg.VCO2_capbank_con.val = 300
		self.reg.int_VCO_ldo0p9_ldo_pu.val = 1
		self.dreg.VCO_5.val = 0
		self.dreg.VCO_6.val = 18
		self.dreg.VCO_9.val = 0
		self.dreg.VCO_10.val = 18
		self.dreg.VCO_13.val = 0xAA
		self.dreg.VCO_25.val = 0
## Set LOGEN regs for 28GHz during init (without multby1p5)
		self.reg.LOGEN_HighBand_sel.val = 0
		self.reg.LOGEN_pu_inputDriver.val =1
		self.dreg.LOGEN_28G_1.val = 252
		self.dreg.LOGEN_28G_2.val = 32
		self.reg.LOGEN_multCtune_28G.val = 0
		self.reg.LOGEN_multbuffbias_28G.val = 2
		self.reg.LOGEN_multbuffCtune_28G.val = 0
		self.reg.LOGEN_PACtune_28G.val = 0
		self.reg.LOGEN_PA1Ibias_28G.val = 23
		self.reg.LOGEN_PA2Ibias_28G.val = 23
##Set regs corresponding to Xtal
		self.dreg.xo_1.val = 64
		self.dreg.xo_2.val = 40
		self.dreg.xo_3.val = 0
		self.dreg.xo_4.val = 0
		self.dreg.xo_5.val = 0
##Set other misc regs
		self.dreg.adc_control_1.val = 0
		self.dreg.adc_control_2.val = 0
		self.dreg.procMon_1.val = 0
		self.dreg.procMon_2.val = 0
		self.dreg.lpo.val = 0
		self.dreg.spare_1.val = 0
		self.dreg.spare_2.val = 0
		self.dreg.spare_3.val = 0
		self.dreg.spare_4.val = 0
		self.dreg.spare_5.val = 0
		self.dreg.spare_6.val = 0
		self.dreg.spare_7.val = 0
		self.dreg.spare_8.val = 0
		return 0 

	def initialize(self, chain=9, loc=0, bypass_reset=False, SPI_length=1):
		self.initialize_FPGA(chain, loc, SPI_length)
		if not bypass_reset or self.simulate_read:
			for reg in self.reg.array:
				reg.val = reg.reset
		self.dreg.bg_6.val = 15
		self.dreg.bg_2.val = 5
		self.run_BG_cal_rtl()
		self.dreg.LF_2.val = 0
		self.dreg.LF_3.val = 1
		self.dreg.mmd_1.val = 33
		self.dreg.pfdcp_1.val = 64
		self.dreg.pfdcp_2.val = 20
		self.dreg.pfdcp_3.val = 10
		self.dreg.pfdcp_4.val = 22
		self.dreg.VCO_1.val = 90
		self.dreg.VCO_2.val = 24
		self.reg.int_VCO_ldo0p9_ldo_pu.val = 1
		self.dreg.VCO_6.val = 18
		self.dreg.VCO_10.val = 18
		self.dreg.VCO_13.val = 0xAA
		self.dreg.xo_1.val = 64
		self.dreg.xo_2.val = 40
		self.logen_pu(band = "LB", pu = 1 , tssi_pu = 0)
		self.set_logen(band="LB", mult_bias=2, buff_bias=1, pa_bias=23, mult_ctune=150, buff_ctune=150, pa_ctune=20)
		return 0

	def run_BG_cal_rtl(self, dbg_prt=False):
		self.reg.bg_en.val = 1
		self.reg.bg_cal_en.val = 1
		self.reg.rcal_delay.val = 4
		self.reg.rcal_start.val = 1
		done = 0
		wait_count = 0
		while (not done) and (wait_count < 10):
			done = self.reg.rcal_done.val
			sleep(0.1)
			wait_count += 1
		pass0_fail1 = self.reg.rcal_fail.val
		if (pass0_fail1) or (wait_count == 10):
			self.reg.bg_override = 1
			self.reg.bg_cal_d.val = 16
			self.reg.bg_override = 0
			print("BG cal failed, setting BG value to mid rail(16)")
		self.reg.bg_cal_en.val = 0
		if (dbg_prt): print("BG cal val = ", self.reg.bg_cal_d.val)
		return self.reg.bg_cal_d.val

	def get_temp_rtl(self, prnt=False):
		self.reg.rd_temp_abort.val = 1
		self.reg.rd_temp_abort.val = 0
		if (prnt): print(("rd_temp_done, before cal = ", self.reg.rd_temp_done.val))
		self.reg.rd_temp_delay.val = 64
		self.reg.rd_temp_start.val = 1
		self.reg.bg_temp_enable.val = 1
		read_done = 0
		while (not read_done):
			read_done = self.reg.rd_temp_done.val
			if (prnt): print(("rd_temp_done = ", read_done))
		chip_temp_comp_val = self.reg.rd_temp_value.val
		chip_temp = round(0.0168 * (chip_temp_comp_val ** 2) - 2.0512 * chip_temp_comp_val + 10.836, 2)
		if (prnt):
			print(("chip temp comp val = %d" % chip_temp_comp_val))
			print(("chip temp = %0.2f" % chip_temp))
		return chip_temp

	def set_logen(self,band = 'LB', mult_bias = 3, buff_bias = 1, pa_bias = 27,mult_ctune = 0, buff_ctune = 0, pa_ctune=0):
		band = band.upper()
		if band not in ["LB","HB"]:
			print("Invalid band selection, choose LB/HB")
			return 0
		freq = '28G' if (band=='LB') else '39G'
		band_set = 1 if (band =="HB") else 0
		getattr(self.reg,"LOGEN_HighBand_sel").val = band_set
		getattr(self.reg,"LOGEN_multGateBias_%s"%freq).val = mult_bias
		getattr(self.reg,"LOGEN_multbuffbias_%s"%freq).val = buff_bias
		getattr(self.reg,"LOGEN_PA1Ibias_%s"%freq).val = pa_bias
		getattr(self.reg,"LOGEN_PA2Ibias_%s"%freq).val = pa_bias
		getattr(self.reg,"LOGEN_multCtune_%s"%freq).val = mult_ctune
		getattr(self.reg,"LOGEN_multbuffCtune_%s"%freq).val = buff_ctune
		getattr(self.reg,"LOGEN_PACtune_%s"%freq).val = pa_ctune
		return 0 

	def save_logen(self,band = 'LB',prnt=True):
		band = band.upper()
		if band not in ["LB","HB"]:
			print("Invalid band selection, choose LB/HB")
			return 0
		freq = '28G' if (band=='LB') else '39G'
		res = []
		blk_set = ['multGateBias','multbuffbias','PA1Ibias','PA2Ibias','multCtune','multbuffCtune','PACtune']
		for i in range(len(blk_set)):
			reg_val = getattr(self.reg,"LOGEN_%s_%s"%(blk_set[i],freq)).val
			res.append(reg_val)
			if prnt:print(blk_set[i]+" = %d"%reg_val)
		return res

	def logen_pu(self, band = "LB", pu = 1 , tssi_pu = 1):
		band = band.upper()
		if band not in ["LB","HB"]:
			print("Invalid band selection, choose LB/HB")
			return 0
		freq = '28G' if (band=="LB") else '39G'
		band_set = 1 if (band =="HB") else 0
		getattr(self.reg,"LOGEN_HighBand_sel").val = band_set
		blk_set = ['mult','multbuffer','PAdr','PAs','PA1','PA2']
		tssi_set = ['mult','multbuff','PAdr','PA1','PA2']
		getattr(self.reg,"LOGEN_pu_inputDriver").val = pu
		for i in range(len(blk_set)):
			getattr(self.reg,"LOGEN_pu_%s_%s"%(blk_set[i],freq)).val = pu
		for j in range(len(tssi_set)):
			getattr(self.reg,"LOGEN_pu_tssi_%s_%s"%(tssi_set[j],freq)).val = tssi_pu
		return 0

	def load_SD_sett(self,
					 ref_in_MHz=122.88,
					 ref_offset_kHz=0,
					 XO_div=1,
					 PFD_dbl_en=1,
					 external=False,
					 freq_out_MHz=4300,
					 prnt = False):
		self.bypass_LF(1)
		xtal_odis = 1 if (external==True) else 0
		self.reg.xo_xtalOdis.val = xtal_odis
		self.reg.SD_reset_sd.val = 1
		self.reg.pfdcp_dbl_en.val = PFD_dbl_en
		self.reg.xo_xtalDiv.val = XO_div
		ref_in_MHz = ref_in_MHz + ref_offset_kHz / 1000.0
		if prnt: print(ref_in_MHz)
		logging.info("Ref in (MHz): {}".format(ref_in_MHz))
		div_ratio = freq_out_MHz / (ref_in_MHz / XO_div *
												(PFD_dbl_en +1 ))
		div_ratio_int = int(div_ratio)
		div_ratio_frac = int((div_ratio - div_ratio_int) * (1 << 30) + 0.5)
		if prnt: print('N=', div_ratio_int, '+ frac=', div_ratio_frac)
		logging.info('N= {} + frac = {} '.format(div_ratio_int, div_ratio_frac))
		if prnt: print('fraction=', (div_ratio_frac + 0.0) / (1 << 30))
		logging.info('fraction = {}'.format((div_ratio_frac + 0.0) / (1 << 30)))
		self.reg.SD_int.val = div_ratio_int
		self.reg.SD_frac.val = div_ratio_frac
		self.reg.SD_reset_sd.val = 0
		self.bypass_LF(0)
		return 0 

	def set_PLL_freq(self,
					 ref_in_MHz=122.88,
					 ref_offset_kHz=0,
					 XO_div=1,
					 PFD_dbl_en=1,
					 external=False,
					 freq_out_MHz=4300,
					 VCO_bias = 18,
					 logen_mult = 1,
					 VCOCALOL = True,
					 CALOL_count_time_in_us = 20,
					 comp_window1=[4, 2048],
					 comp_window2=[2, 16384],
					 vco_sel_ovr = False,
					 vco_sel_ovr_val = 1,
					 LF_DC = 128,
					 prnt = False):
		if (logen_mult == 1):
			band , div_ratio = "LB",1
			getattr(self.reg,"LOGEN_multby1p5_28G").val = 0
		elif (logen_mult == 1.5):
			band, div_ratio = "LB",1
			getattr(self.reg,"LOGEN_multby1p5_28G").val = 1
		else :
			band, div_ratio = "HB",1
			getattr(self.reg,"LOGEN_multby1p5_28G").val = 0
		band_comp = "HB" if (band=="LB") else "LB"
		self.logen_pu(band = band_comp, pu = 0 , tssi_pu = 0)
		self.logen_pu(band = band, pu = 1 , tssi_pu = 1)
		self.load_SD_sett(ref_in_MHz = ref_in_MHz,ref_offset_kHz = ref_offset_kHz, XO_div=XO_div, PFD_dbl_en = PFD_dbl_en, external = external, freq_out_MHz = freq_out_MHz/logen_mult, prnt = prnt)
		if VCOCALOL:
			countref = int(0.5+0.1*ref_in_MHz*CALOL_count_time_in_us)
			countval_targ = int(0.5+countref*freq_out_MHz/logen_mult/(2*ref_in_MHz))
			start_delay = int(5*ref_in_MHz+0.5)
			pause_cnt = int(ref_in_MHz+0.5)
			self.vcocal_sett(start_delay = start_delay, countref = countref,countval_targ = countval_targ, pause_cnt = pause_cnt, vco_sel_threshold = 0)
			self.run_vco_olc(vco_sel_ovr = vco_sel_ovr, vco_sel_ovr_val = vco_sel_ovr_val ,LF_DC = LF_DC,prnt_instr = False)
		else:
			self.run_PLL_cal(comp_window1=comp_window1, comp_window2=comp_window2,vco_sel_ovr = vco_sel_ovr,vco_sel_ovr_val = vco_sel_ovr_val, prnt=prnt)
		return 0 

	def run_PLL_cal(self,
					comp_window1=[4, 2048],
					comp_window2=[2, 16384],
					vco_sel_ovr = False,
					vco_sel_ovr_val = 1 ,
					prnt = False):
		successful = False
		if (vco_sel_ovr == True):
			spare1=self.reg.spare_spare1.val
			self.reg.VCOCALOL_vco_sel_ovr.val = 1
			self.reg.VCOCALOL_vco_sel_ovr_val.val = spare1*(vco_sel_ovr_val - 1)
			vco_num = vco_sel_ovr_val
		else:
			vco_num = (getattr(self.reg,"VCOCALOL_vcoSel_val").val)+1
		self.vco_sel(vco_num = vco_num)
		self.set_LF_comp_thresholds(comp_window1[0], comp_window1[1])
		for i in range(2):
			self.cap_search_rtl(mode = i,vco = vco_num)
			sleep(0.1)
			PLL_lock_status = self.get_PLL_lock_status()
			if (PLL_lock_status == c.PllLockModes.Locked or PLL_lock_status == c.PllLockModes.Illegal):
				successful = True
				if (prnt==True):
					print("Lock_mode = %d & Cap_code = %d"%(i,getattr(self.reg,"VCO%d_capbank_con"%vco_num).val))
				break
		if(successful != True):
			self.set_LF_comp_thresholds(comp_window2[0], comp_window2[1])
			for i in range(2):
				self.cap_search_rtl(mode = i,vco = vco_num)
				PLL_lock_status = self.get_PLL_lock_status()
				if (PLL_lock_status == c.PllLockModes.Locked or PLL_lock_status == c.PllLockModes.Illegal):
					successful = True
					if (prnt==True):
						print("Comp Threshold Changed\nLock_mode = %d & Cap_code = %d"%(i,getattr(self.reg,"VCO%d_capbank_con"%vco_num).val))
					break

	def cap_search_rtl(self,mode = 0,vco = 1):
		self.reg.VCO1_capbank_con.val=1023
		self.reg.VCO2_capbank_con.val=1023
		self.reg.vco_cap_ctrl_abort.val = 1
		self.reg.vco_cap_prescale_cfg.val = 127
		self.reg.vco_cap_settle_cfg.val = 127
		self.reg.vco_cap_restart_cfg.val = 1048575 
		self.reg.vco_cap_ctrl_linear.val = mode
		self.reg.vco_cap_ctrl_abort.val = 0
		#self.reg.vco_cap_ctrl_sel.val = (vco-1)
		self.reg.vco_cap_ctrl_start.val = 1
		return

	def bypass_LF(self, bypass=1, DC=0x8000):
		self.reg.LF_bypass.val = bypass
		self.reg.pfdcp_openLoop.val = bypass
		self.reg.LF_bypass_DC.val = DC
		return 0

	def get_PLL_lock_status(self,comp_window=[2, 16384]):
		self.set_LF_comp_thresholds(comp_window[0], comp_window[1])
		comp1 = self.reg.LF_compOut1.val
		comp2 = self.reg.LF_compOut2.val
		if comp1 == 0 and comp2 == 0:
			status = c.PllLockModes.Unlocked_low
		elif comp1 == 1 and comp2 == 0:
			status = c.PllLockModes.Locked
		elif comp1 == 0 and comp2 == 1:
			status = c.PllLockModes.Illegal
		else:
			status = c.PllLockModes.Unlocked_high
		return status

	def get_PLL_Vctrl(self):
		for i in range(16):
			self.reg.LF_Detector1con.val=2**i
			comp1 = self.reg.LF_compOut1.val
			if (comp1==0):
				break
		Vctrl=(1.5*math.log2(2**i)/32)+(1.5*math.log2(2**(i-1))/32)
		return Vctrl

	def set_LF_comp_thresholds(self, comp1=4, comp2=2048):
		self.reg.LF_Detector1con.val = comp1
		self.reg.LF_Detector2con.val = comp2
		return 0

	def vcocal_sett(self, start_delay = 500, countref = 246,countval_targ = 5000, pause_cnt = 100, vco_sel_threshold = 0):
		self.reg.VCOCALOL_startDelay.val = start_delay
		self.reg.VCOCALOL_countRef.val = countref
		self.reg.VCOCALOL_countVal_targ.val = countval_targ
		self.reg.VCOCALOL_pauseCnt.val = pause_cnt
		self.reg.VCOCALOL_vcoSelThresh.val = vco_sel_threshold
		return 0

	def vco_sel_rtl(self , prnt = True):
		self.vcocal_sett()
		self.reg.VCOCALOL_abort.val = 1
		self.reg.VCOCALOL_vco_sel_ovr.val = 0
		self.reg.VCOCALOL_use_vcocalol_capval.val = 1
		self.reg.VCOCALOL_xtalbuf_pu.val = 1
		self.reg.VCOCALOL_vcoSelEn.val = 1
		done = 0
		cntr = 0
		while (not done):
			done = self.reg.VCOCALOL_vcoSel_done.val
			sleep(0.01)
			cntr+=1
			if(cntr>100):
				print("VCO Selection failed, VCO not selected")
				self.reg.VCOCALOL_abort.val = 1
				self.reg.VCOCALOL_vcoSelEn.val = 0
				return
		vco_cnt = getattr(self.reg,"VCOCALOL_vcoCnt_val").val
		vco_num = getattr(self.reg,"VCOCALOL_vcoSel_val").val
		self.reg.VCOCALOL_vcoSelEn.val = 0
		self.reg.VCOCALOL_vco_sel_ovr_val.val = 1
		if (prnt):print("VCO Selection Complete with VCO_Cnt = %d, selected VCO = %d"%(vco_cnt,vco_num+1))
		return (vco_num+1)

	def run_vco_olc(self,vco_sel_ovr = False, vco_sel_ovr_val = 1 , LF_DC = 128,prnt_instr = False):
		if (prnt_instr == True):
			print('Function parameters for open loop cal are as follows:\n\
			vco_sel_ovr = True - enable VCO selection overide , False - use VCO selction from VCO_SEL_RTL\n\
			vco_sel_ovr_val: = - selects VCO 1 for open loop cal , 2 - selects VCO 2 for open loop cal')
			return 0 
		self.reg.VCOCALOL_abort.val = 0
		self.reg.LF_bypass_DC.val=LF_DC
		if (vco_sel_ovr == True):
			spare1=self.reg.spare_spare1.val
			self.reg.VCOCALOL_vco_sel_ovr.val = 1
			self.reg.VCOCALOL_vco_sel_ovr_val.val = spare1*(vco_sel_ovr_val - 1)
			vco_num = vco_sel_ovr_val
		else:
			vco_num = (getattr(self.reg,"VCOCALOL_vcoSel_val").val)+1
		self.vco_sel(vco_num = vco_num)
		self.reg.VCOCALOL_use_vcocalol_capval.val = 1
		self.reg.VCOCALOL_xtalbuf_pu.val = 1
		self.reg.VCOCALOL_enable.val = 1
		done = 0
		cntr = 0
		while (not done):
			cntr +=1
			done = self.reg.VCOCALOL_olc_done.val
			sleep(0.01)
			if(cntr>100):
				print("VCO Open Loop Cal failed")
				self.reg.VCOCALOL_abort.val = 1
				self.reg.VCOCALOL_enable.val = 0
				return
		self.reg.VCOCALOL_cap_copy_over.val = 1
		self.reg.VCOCALOL_enable.val = 0
		self.reg.VCOCALOL_use_vcocalol_capval.val = 0
		self.reg.VCOCALOL_xtalbuf_pu.val = 0
		return getattr(self.reg,"VCOCALOL_vco%d_capbank_con"%vco_num).val

	def vco_bias_sel(self, pkdet_code = 1, initial_bias = 18, vco_sel_ovr = False, vco_sel_ovr_val = 1 ,prnt_instr = False):
		if (prnt_instr == True):
			print('Function parameters for VCO_BIAS_CAL are as follows:\n\
			vco_sel_ovr = True - enable VCO selection overide , False - use VCO selction from VCO_SEL_CAL\n\
			vco_sel_ovr_val = 1 - selects VCO 1 for open loop cal , 2 - selects VCO 2 for open loop cal\n\
			pkdet_code = peak detector code for desired swing\n\
			initial_bias = Initial value of VCO bias (user defined)\n\
			To change other parameters such as bias_settle_time- make changes on pyreg')
			return 0
		if (vco_sel_ovr == True):
			self.reg.VCOCALOL_vco_sel_ovr.val = 1
			self.reg.VCOCALOL_vco_sel_ovr_val.val = (vco_sel_ovr_val - 1)
			vco_num = vco_sel_ovr_val
		else:
			vco_num = (getattr(self.reg,"VCOCALOL_vcoSel_val").val)+1
		self.reg.VCO_bias_cal_abort.val = 0
		getattr(self.reg,"VCO%s_pkdet_con"%vco_num).val = pkdet_code
		getattr(self.reg,"VCO%s_bias_val"%vco_num).val=initial_bias
		self.vco_sel(vco_num = vco_num)
		self.reg.VCO_bias_settle_time.val = 100
		self.reg.VCO_bias_cal_en.val = 1
		done = 0
		cntr = 0
		while (not done):
			done = self.reg.VCO_bias_cal_done.val
			sleep(0.01)
			if(cntr>100):
				print("VCO Open Loop Cal failed")
				self.reg.VCO_bias_cal_abort.val = 1
				self.reg.VCO_bias_cal_en.val = 0
				return -1
			self.reg.VCO_bias_cal_en.val = 0
		return getattr(self.reg,"VCO%d_bias_val"%vco_num).val

	def vco_sel(self,vco_num = 1):
		#spare1=self.reg.spare_spare1.val
		#self.reg.VCOCALOL_vco_sel_ovr.val=1
		#self.reg.VCOCALOL_vco_sel_ovr_val.val=spare1*(vco_num - 1)
		vco_comp = 2 if (vco_num==1) else 1
		getattr(self.reg,"VCO_pu_VCO%s"%vco_comp).val = 0
		getattr(self.reg,"VCO_pu_pkdet%s"%vco_comp).val = 0
		getattr(self.reg,"VCO_pu_VCO%s"%vco_num).val = 1
		getattr(self.reg,"VCO_pu_pkdet%s"%vco_num).val = 1
		return 0 

	def clear_ana_mux(self):
		self.dreg.test_ctrl.val = 0
		return 0

	def set_ana_mux(self, option='MMD',prnt_instr=False):
		mux_dict = {"none":0,
					"adc_0":1,
					"adc_1":2,
					"logen":3,
					"vco":4,
					"mmdiv":5,
					"pfdcp":6,
					"xo":7,
					"amux_vdd0p9":8,
					"amux_ana_vgn":9,
					"amux_ana_vgp":10,
					"vddcldo_0":11,
					"vddcldo_1":12,
					"vddcldo_2":13,
					"vddcldo_3":14,
					"xo_buff":15,
					"vco_ldo":16
					}
		option = option.lower()
		self.clear_ana_mux()
		if ((option not in mux_dict.keys()) or (prnt_instr == True)):
			print("Choose from the mux options below")
			for k,v in mux_dict.items():
				print(k,v)
			return
		elif(option in mux_dict.keys()):
			self.dreg.test_ctrl.val = mux_dict[option]
		return

	def enable_tssi(self, block="HB_TSSI_MULT"):
		block = block.upper()
		if(block in list(self.blk_dict.keys())):
			getattr(self.reg, self.blk_dict[block][0]).val = 1
			getattr(self.reg,"adc_sel_reg").val = self.blk_dict[block][1]
			getattr(self.reg,"int_LOGEN_TestMux_sel").val = self.blk_dict[block][2]
		else:
			print("%s is not a valid block selection; valid blocks are:" % block)
			for b in list(self.blk_dict.keys()):
				print(b)
		return 0

	def clear_tssi(self):
		for b in self.blk_dict.keys():
			getattr(self.reg,"%s"%self.blk_dict[b][0]).val = 0
		getattr(self.reg,"adc_sel_reg").val = 0
		getattr(self.reg,"int_LOGEN_TestMux_sel").val = 0
		return 0 

	def read_tssi(self, vref=0, slope_offset=None, return_format='ADC', clk_div=32, cycles=32, prnt=False):
		if slope_offset:
			slope = slope_offset[0]
			offset = slope_offset[1]
		else:
			if vref == 0:
				slope = 0.34
				offset = -32
			# slope = 3.7202
			# offset= -25.727
			else:
				# 6.1722x + 66.478
				slope = 6.1722
				offset = 66.478
		self.reg.adc_ref_sel.val = vref
		return_list = []
		# self.reg.adc_settle_cycles.val = cycles
		self.reg.adc_clk_div.val = clk_div
		self.dreg.adc_control_1.val |= 1
		
		c = 0
		while c < 10 and self.reg.adc_sel_reg.val != self.reg.adc_valid_reg.val:
			sleep(0.5)
			c += 1
		if c == 10:
			print("ADC read timeout")
			return return_list
		read_list = ['LB_TSSI_PA2', 'LB_TSSI_PA1', 'LB_TSSI_PAdr', 'LB_TSSI_BUFF', 'LB_TSSI_MULT', 'LB_VDD0P9_PA', 
					 'HB_TSSI_PA2', 'HB_TSSI_PA1', 'HB_TSSI_PAdr', 'HB_TSSI_BUFF', 'HB_TSSI_MULT', 'HB_VDD0P9_PA']
		selection = self.reg.adc_sel_reg.val
		for i in range(len(read_list)):
			if (selection >> i) & 1:
				readout = getattr(self.reg, "adc_reg_%d" % i).val
				if prnt:
					print(read_list[i], readout)
				if return_format.upper() != 'ADC':
					return_list.append(slope*readout + offset)
				else:
					return_list.append(readout)
		return return_list

	def set_tssi_params(self, vref=0, clk_div = 32):
		self.reg.adc_ref_sel.val = vref
		self.reg.adc_clk_div.val = clk_div
		self.reg.adc_abort.val = 1
		self.reg.adc_abort.val = 0
		return 0 

	def read_tssi_fast(self):
		self.reg.adc_start.val = 1
		sleep(0.005)
		readout = getattr(self.reg, "adc_reg_0").val
		return readout

	def gss_cap_tune(self,f, a , b ,tol=1e-5,cap_reg="LOGEN_multCtune_28G",h=None, c=None, d=None, fc=None, fd=None):
		(a , b) = (min(a,b),max(a,b))
		if h is None: h = b-a
		if h <= tol: return int((a+b)/2)
		if c is None: c = int(b - (gr*h))
		if d is None: d = int (a +(gr*h))
		if fc is None:
			getattr(self.reg,"%s"%cap_reg).val = c
			fc = self.read_tssi_fast()
		if fd is None:
			getattr(self.reg,"%s"%cap_reg).val = d
			fd = self.read_tssi_fast()
		print(a,b,h,c,fc,d,fd)
		if fc > fd:
			return self.gss_cap_tune(f,a,d,tol,cap_reg,h=None, c=None, fc=None, d=c, fd=fc)
		else:
			return self.gss_cap_tune(f,c,b,tol,cap_reg,h=None, c=d, fc=fd, d=None, fd=None)

	def logen_cal(self, tssi_out_lim = 965, band_overide = None, prnt=False):
		size_dict = {"LB":{"LOGEN_multGateBias_28G":[0,8,1],
						   "LOGEN_multbuffbias_28G":[0,8,1],
						   "LOGEN_PA1Ibias_28G":[8,32,1],
						   "LOGEN_multCtune_28G":[0,256,1],
						   "LOGEN_multbuffCtune_28G":[0,256,1],
						   "LOGEN_PACtune_28G":[0,32,1],
						   "init_bias_1" : [5,5,25],
						   "init_bias_2" : [3,2,16]
						   },
					 "HB":{"LOGEN_multGateBias_39G":[0,8,1],
						   "LOGEN_multbuffbias_39G":[0,8,1],
						   "LOGEN_PA1Ibias_39G":[8,32,1],
						   "LOGEN_multCtune_39G":[0,16,1],
						   "LOGEN_multbuffCtune_39G":[0,16,1],
						   "LOGEN_PACtune_39G":[0,16,1],
						   "init_bias_1" : [10,10,20],
						   "init_bias_2" : [10,3,10]
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
		tssi_blk_set = ['%s_TSSI_MULT'%band,'%s_TSSI_BUFF'%band,'%s_TSSI_PA1'%band]
		self.logen_pu(band = band_comp, pu = 0 , tssi_pu = 0)
		self.logen_pu(band = band, pu = 1 , tssi_pu = 1)
		tssi_out_low = tssi_out_lim*0.99
		tssi_out_high = tssi_out_lim*1.01
		self.set_ana_mux(option="logen")
		self.set_logen(band = band, mult_bias = size_dict[band]["init_bias_1"][0], buff_bias = size_dict[band]["init_bias_1"][1], pa_bias = size_dict[band]["init_bias_1"][2], mult_ctune = 50, buff_ctune = 50, pa_ctune=10)
		self.set_tssi_params(vref=0, clk_div = 32)
		for i in range(len(cap_reg_list)):
			self.enable_tssi(block=tssi_blk_set[i])
			cap_start = size_dict[band][cap_reg_list[i]][0]
			cap_stop = size_dict[band][cap_reg_list[i]][1]
			cap_step = size_dict[band][cap_reg_list[i]][2]
			cap_list = list(numpy.arange(cap_start,cap_stop,cap_step))
			max_cap_val = self.gss_cap_tune(cap_list, cap_list[0] , cap_list[-1] ,tol=1,cap_reg = cap_reg_list[i],h=None, c=None, d=None, fc=None, fd=None)
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
				readout =self.read_tssi_fast()
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
