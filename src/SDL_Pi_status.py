import SDL_Pi_SunControl as sdl

sc = sdl.SDL_Pi_SunControl(
    INA3221Address = 0x40,
    USBControlEnable = 26,
    USBControlControl = 21,
    WatchDog_Done = 13,
    WatchDog_Wake = 16
)

print('SDL_Pi_SunControl Power Status\n')

batteryVoltage = sc.readChannelVoltageV(sdl.SunControl_LIPO_BATTERY_CHANNEL)
batteryCurrent = sc.readChannelCurrentmA(sdl.SunControl_LIPO_BATTERY_CHANNEL)
print(f'LiPo Battery: \t {batteryVoltage:3.2f} V / {batteryCurrent:3.2f} mA')
# TODO Battery SoC

solarCellVoltage = sc.readChannelVoltageV(sdl.SunControl_SOLAR_CELL_CHANNEL)
solarCellCurrent = sc.readChannelCurrentmA(sdl.SunControl_SOLAR_CELL_CHANNEL)
print(f'Solar Cells: \t {solarCellVoltage:3.2f} V / {solarCellCurrent:3.2f} mA')

piVoltage = sc.readChannelVoltageV(sdl.SunControl_OUTPUT_CHANNEL)
piCurrent = sc.readChannelCurrentmA(sdl.SunControl_OUTPUT_CHANNEL)
print(f'Pi: \t {piVoltage:3.2f} V / {piCurrent:3.2f} mA')
